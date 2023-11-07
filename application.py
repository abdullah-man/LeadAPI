from fastapi import FastAPI, Body, Depends 
from fastapi import UploadFile, File
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field, EmailStr
import uvicorn

from db_operations import DbOperation
from extraction import extractor
from predict import Predict
from db_warehouse import warehouse_dump

import pandas as pd
import copy
import pickle
import os
from secrets import token_hex # for hashing uploaded file name
import psycopg2

from app.auth.jwt_handler import signJWT
from app.auth.jwt_bearer import jwtBearer  


class Settings(BaseSettings):
    """
    Saves database connection information in environment variables
    """
    db_connection_info : dict = {'database' : 'postgres', 'user' : 'postgres',
                                  'password' : 'axiom123', 'host' : '0.0.0.0', 
                                  'port' : '5432'}
    db_data_table_name : str = 'information'


# ---------------------- Models ---------------------------

class Lead(BaseModel):
    """
    Model of the lead object passed as JSON object in POST request to label_fetch 
    """
    lead : str
    db_model_name : str

class ModelDetails(BaseModel):
    """
    Model containing ml model name details
    """
    db_model_name : str


class UserSchema(BaseModel):
    fullname : str = Field(default=None)
    email : EmailStr = Field(default=None) # EmailStr is an email validator
    password : str = Field(default=None)
    class Config:
        the_schema = {
            "user_demo" :{
                "name" : "abc",
                "email" : "abc@abc.com",
                "password" : "123"
            }
        }


class UserLoginSchema(BaseModel):
    email : EmailStr = Field(default=None) # EmailStr is an email validator
    password : str = Field(default=None)
    class Config:
        the_schema = {
            "user_demo" :{
                "email" : "abc@abc.com",
                "password" : "123"
            }
        }

# ---------------------------------------------------------------

users = []  # temporarily for authentication . Later in DB


settings = Settings()
app = FastAPI()


# ------------------------- Routes -------------------------------

@app.get("/data_fetch", dependencies=[Depends(jwtBearer())])
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


@app.post("/label_fetch", dependencies=[Depends(jwtBearer())])
async def label_fetch(rss_feed : Lead):
    """
    Receives a lead in json format, extracts embedded information,
    classify it using ML model, saves it in datawarehouse,
    returns as dict with label info to the client
    """
    # getting json file sent through the post request data parameter
    rss_feed = rss_feed.model_dump_json()

    # type casting str into dict
    rss_feed = eval(rss_feed)
    feed = rss_feed['lead'] # extracting rss feed text 
    model_name = rss_feed['db_model_name'] # extracting model name 
    # extract embedded info
    extracted_info = extractor(feed=feed)

    # ---
    # load ml model from database
    conn_info = settings.db_connection_info

    sql = f"SELECT model_file FROM model WHERE model_name = %s" 
    value = (model_name,)

    db_op = DbOperation()
    model_file = db_op.fetch_model(conn_info=conn_info, sql=sql, value=value)
    # ---

    # Deserializing the model file
    ml_model = pickle.load(open(model_file, 'rb'))

    # predict the label
    pr = Predict()
    # deepcopying, as mutable objects are passed by reference. 
    # extracted_info gets changed on passing as arg.
    encoded_info = pr.encode_lead(data=copy.deepcopy(extracted_info)) 
    vec = pr.vectorize_lead(encoded_info)
    predicted_label = pr.predict_lead(vector=vec, ml_model=ml_model)

    # save data into data-warehouse/database
    warehouse_dump(info_dict=extracted_info, label=predicted_label, table_name=settings.db_data_table_name)

    # send back to the client : HQ with label information
    extracted_info['label'] = predicted_label
    print(extracted_info)
    return extracted_info


@app.post("/model_upload", dependencies=[Depends(jwtBearer())])
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


@app.put("/update_model")
async def model_update():
    pass


@app.delete("/model_delete", dependencies=[Depends(jwtBearer())])
async def model_delete(model_details : ModelDetails):
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

# user sign up - to create a new user
@app.post("/user/signup", tags=["user"])
def user_signup(user : UserSchema = Body(default=None)):
    users.append(user) # add the user to the database
    return signJWT(user.email) # that's why we need to install email validator from pydantic

# checks if a user already exists before creating a jwt with the user email
def check_user(data : UserLoginSchema): # UserLoginSchema has email and password
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
        return False

# login
@app.post("/user/login", tags=["user"])
def user_login(user : UserLoginSchema = Body(default=None)):
    # we also want to return signJWT with the user email as the user has already sugned up and
    # registered with his email
    if check_user(user):
        return signJWT(user.email)
    else:
        return {"error" : "invalid login details"}




if __name__== '__main__':
    uvicorn.run("application:app", host="127.0.0.1", port=8000, reload=True)
