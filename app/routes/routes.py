import pandas as pd
import copy
import pickle
import os
from secrets import token_hex # for hashing uploaded file name
import psycopg2

from fastapi import Body, Depends, APIRouter 
from fastapi import UploadFile, File
from pydantic import BaseSettings

from extraction import extractor
from predict import Predict
from app.database.db_operations import DbOperation
from app.database.db_warehouse import warehouse_dump
from app.auth.jwt_handler import signJWT
from app.auth.jwt_bearer import jwtBearer  
from app.models.models import Lead, MLModel, UserLogin, Users, Record
from app.database.connection import engine_url, get_session, conn
from sqlmodel import select, Session


class Settings(BaseSettings):
    """
    Saves database connection information in environment variables
    """
    db_connection_info : dict = {'database' : 'postgres', 'user' : 'postgres',
                                  'password' : 'axiom123', 'host' : '0.0.0.0', 
                                  'port' : '5432'}
    db_data_table_name : str = 'information'
    db_users_table_name : str = 'users'



settings = Settings()
routes_router = APIRouter(tags=["routes"])




@routes_router.get("/data_fetch", dependencies=[Depends(jwtBearer())])
async def data_fetch():
    """
    Fetches all data from the database and returns as JSON in response
    """
    conn_info = settings.db_connection_info
    table_name = settings.db_data_table_name
    
    data_fetcher = DbOperation()
    sql = f"SELECT * FROM {table_name}"
    data = data_fetcher.fetch_data(conn_info=conn_info, sql=sql)

    cols = ['posted_on', 'category', 'skills', 'country', 'message', 'hourly_from', 'hourly_to', 'budget', 'label', 'id']
    data = pd.DataFrame(data=data, columns=cols)
    data = data.to_dict()
    return data


@routes_router.post("/label_fetch", dependencies=[Depends(jwtBearer())])
async def label_fetch(rss_feed : Lead):
    """
    Receives a lead in json format, extracts embedded information,
    classify it using ML model, saves it in datawarehouse,
    returns as dict with label info to the client
    """
    # getting json file sent through the post request data parameter
    # model_dump() -> converts a pydantic model to dictionary object
    rss_feed = rss_feed.model_dump_json()
    rss_feed = eval(rss_feed)
    model_name = rss_feed['db_model_name']

    # load ml model from database
    conn_info = settings.db_connection_info
    sql = f"SELECT model_file FROM model WHERE model_name = %s" 
    value = (model_name,)

    db_op = DbOperation()
    model_file = db_op.fetch_model(conn_info=conn_info, sql=sql, value=value)
    # unhash the model file name  

    # Deserializing the model file
    ml_model = pickle.load(open(model_file, 'rb'))

    # predict the label
    pr = Predict()
    # deepcopying, as mutable objects are passed by reference. 
    # extracted_info gets changed on passing as arg.
    encoded_info = pr.encode_lead(data=copy.deepcopy(rss_feed)) 
    vec = pr.vectorize_lead(encoded_info)
    predicted_label = pr.predict_lead(vector=vec, ml_model=ml_model)

    # save data into data-warehouse/database
    warehouse_dump(info_dict=rss_feed, label=predicted_label, table_name=settings.db_data_table_name)

    # send back to the client : HQ with label information
    rss_feed['label'] = predicted_label
    # print("Extracted Info from label_fetch : \n",extracted_info)
    return rss_feed


@routes_router.post("/model_upload", dependencies=[Depends(jwtBearer())])
async def model_upload(file : UploadFile = File(...)):
    file_extension = file.filename.split(".").pop()
    model_name = file.filename.split(".")[0]
    hashed_file_name = token_hex(10) # name size 10 bytes
    new_file_name = f"{hashed_file_name}.{file_extension}"
    file_path = os.path.join("models",new_file_name)
    
    # save file on server
    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)

    # save model's file_path in database
    db_op = DbOperation()
    sql = "INSERT INTO model (model_name, model_file) VALUES (%s, %s)"
    values = (model_name, file_path)
    db_op.save_model(conn_info=settings.db_connection_info, sql=sql, values=values)

    return {"status" : "Success", "message" : "Model saved successfully!"}


@routes_router.put("/update_model")
async def model_update():
    pass


@routes_router.delete("/model_delete", dependencies=[Depends(jwtBearer())])
async def model_delete(model_details : MLModel):
    # getting json file sent through the post request data parameter
    model_details = model_details.model_dump_json()

    # type casting str into dict
    model_details = eval(model_details)
    model_name = model_details['model_name']

    # fetching model file path from db
    # load ml model from database
    conn_info = settings.db_connection_info

    sql = f"SELECT model_file FROM model WHERE model_name = %s" 
    value = (model_name,)

    db_op = DbOperation()
    model_file = db_op.fetch_model(conn_info=conn_info, sql=sql, value=value)
    
    # Deleting the model from Database
    try:
        sql = f"DELETE FROM model WHERE model_name = %s" 
        value = (model_name,)
        db_op.delete_model(conn_info=conn_info, sql=sql, value=value)

    except (Exception, psycopg2.DatabaseError) as e:
        return {'status' : 'Failed', 'message' : 'Model could not be deleted from database', 'exception' : e}

    # Deleting the model file from server
    try:
        os.remove(model_file)
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
    
    # for user in all_users:
    #     print(user)
    #     print(type(user))

    for user in all_users:
        if caller_flag=='signup':
            if user.email == data.email:
                USER_PRESENT = True
                print("**** user found in signup : ",user.email)
                return USER_PRESENT
        elif caller_flag=='login':
            if user.email == data.email and user.password == data.password:
                USER_PRESENT = True
                print("**** user found in login : ", user.email)
                return USER_PRESENT
        elif caller_flag != 'signup' or caller_flag != 'login':
            return {"error" : "caller flag not set either signup or login"}
    print("**** No where USER found")
    return USER_PRESENT


# user sign up - to create a new user
@routes_router.post("/user/signup", tags=["user"])
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
