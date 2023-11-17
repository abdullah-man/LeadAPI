import copy
import pickle
import os
from secrets import token_hex # for hashing
from typing import List

from fastapi import Body, Depends, APIRouter 
from fastapi import UploadFile, File
from sqlmodel import select, Session

from app.auth.jwt_handler import signJWT
from app.auth.jwt_bearer import jwtBearer  
from app.models.models import Lead, MLModel, UserLogin, Users, Record, MLModelDelete
from app.database.connection import get_session
from app.predict.predict import Predict 



routes_router = APIRouter(tags=["routes"])



@routes_router.get("/data_fetch", dependencies=[Depends(jwtBearer())], response_model=List[Record])
async def data_fetch(session=Depends(get_session)):
    """
    Fetches all data from the database and returns as JSON in response
    """
    statement = select(Record)
    all_records = session.exec(statement).all() # .all() gives a list of the returned query set

    return all_records


@routes_router.post("/label_fetch", dependencies=[Depends(jwtBearer())])
async def label_fetch(rss_feed : Lead, session=Depends(get_session)):
    """
    Receives a lead in json format,
    classify it using ML model, saves it in datawarehouse,
    returns as dict with label info to the client
    """
    # get model from the database and unpickle the model file for inference
    try:
        statement = select(MLModel).where(MLModel.model_name==rss_feed.model_name)
        model = session.exec(statement).one()
        model = pickle.load(open(model.model_file, 'rb'))

        pr = Predict()
        # encode the lead
        encoded_info = pr.encode_lead(data=copy.deepcopy(rss_feed.dict())) # pass as a dictionary
        # vectorize the lead
        vec = pr.vectorize_lead(encoded_info)
        # predict the lead
        predicted_label = pr.predict_lead(vector=vec, ml_model=model)
    except(Exception) as e:
        return {"error" : "prediction could not be carried out", "detail" : e}
    
    # save the lead as Record object in the data-warehouse
    try:
        record = Record(
            posted_on=rss_feed.posted_on,
            category=rss_feed.category,
            skills=rss_feed.skills,
            country=rss_feed.country,
            message=rss_feed.message,
            hourly_from=rss_feed.hourly_from,
            hourly_to=rss_feed.hourly_to,
            budget=rss_feed.budget,
            label=predicted_label
        )
        session.add(record)
        session.commit()
    except(Exception) as e:
        return{"error" : "record could not be saved in the warehouse", "detail" : e}
    
    # return the label
    return {'label' : predicted_label}


@routes_router.post("/model_upload", dependencies=[Depends(jwtBearer())])
async def model_upload(file : UploadFile = File(...), session=Depends(get_session)):
    file_extension = file.filename.split(".").pop()
    model_name = file.filename.split(".")[0]
    
    # check if a model under this name already exists in the database
    statement = select(MLModel)
    fetched_models = session.exec(statement)
    for model in fetched_models:
        if model.model_name == model_name:
            return {"Error" : "Cannot upload the model as another model under this name already exists."}

    hashed_file_name = token_hex(10) # name size 10 bytes
    new_file_name = f"{hashed_file_name}.{file_extension}"
    file_path = os.path.join("models",new_file_name)
    
    # save file on server
    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)

    # # save model's file_path in database
    ml_model = MLModel(model_name=model_name, model_file=file_path)
    session.add(ml_model)
    session.commit()
    session.refresh(ml_model)
    return {"success" : "ml model has successfully uploaded"}


@routes_router.delete("/model_delete", dependencies=[Depends(jwtBearer())])
async def model_delete(model_details : MLModelDelete, session=Depends(get_session)):
    # fetch the model and delete from DB
    try:
        statement = select(MLModel).where(MLModel.model_name==model_details.model_name)
        model = session.exec(statement).one()
        model_path = model.model_file
        session.delete(model)
        session.commit()
    except Exception as e:
        pass 
    # Delete model file from Server        
    try:
        os.remove(model_path)
    except (Exception, FileNotFoundError) as e:
        return {'status' : 'Failed', 'message' : 'Model file could not be deleted from server', 'exception' : e}

    return {'status' : 'Success', 'message' : 'Model deleted from database and server successfully'}


# --------------- Signup - Login Routes -------------------
# checks if a user already exists in the database before signup or login
def check_user(data : UserLogin, caller_flag : str, session : Session) -> bool: # UserLoginSchema has email and password
    """ 
    fetches all users from db and check presence of the passed user as data argument.
    args:
        data : 
        caller_flag :
        session : Session object, as passed by signup or login function. 
    """
    USER_PRESENT = False
    statement = select(Users)
    all_users = session.exec(statement)

    for user in all_users:
        if caller_flag=='signup':
            if user.email == data.email:
                USER_PRESENT = True
                return USER_PRESENT
        elif caller_flag=='login':
            if user.email == data.email and user.password == data.password:
                USER_PRESENT = True
                return USER_PRESENT
        elif caller_flag != 'signup' or caller_flag != 'login':
            return {"error" : "caller flag not set either signup or login"}
    print("**** No where USER found")
    return USER_PRESENT


# user sign up - to create a new user
# include_in_schema=Flase -> hides the endpoint from the generated OpenAPI schema and from auto documentation
@routes_router.post("/user/signup", tags=["user"], include_in_schema=False) 
def user_signup(user : Users = Body(default=None), session=Depends(get_session)):
    if not check_user(user, caller_flag='signup', session=session): # if USER_PRESENT is False
        # insert new user in the DB
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"success" : "user has successfully signed up"}
    else:
        return {"notification" : "user already exists"}


# login
@routes_router.post("/user/login", tags=["user"])
def user_login(user : UserLogin = Body(default=None), session=Depends(get_session)):
    # we also want to return signJWT with the user email as the user has already sugned up and
    # registered with his email
    if check_user(user, caller_flag='login', session=session):
        return signJWT(user.email)
    else:
        return {"error" : "invalid login details"}
