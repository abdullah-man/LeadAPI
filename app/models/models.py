from pydantic import BaseModel, Field, EmailStr
from typing import Union, Optional
from sqlmodel import SQLModel, Field, Column
# from sqlalchemy import Column, Integer, Float

class Lead(BaseModel):
    """
    Model of the lead object passed as JSON object in POST request to label_fetch 
    """
    posted_on : str
    category : str
    skills : str
    country : str
    message : str
    hourly_from : Union[float, str] # either float or string
    hourly_to : Union[float, str]
    budget : Union[float, str]
    model_name : str
    class Config:
        the_schema = {
            "lead_demo" :{
                "posted_on" : "<p>this is a lead</p>",
                "category" : "<p>this is a lead</p>",
                "skills" : "<p>this is a lead</p>",
                "country" : "<p>this is a lead</p>",
                "message" : "<p>this is a lead</p>",
                "hourly_from" : "float or empty string",
                "hourly_to" : "float or empty string",
                "budget" : "float or empty string",
                "db_model_name" : "jkl_v0",
            }
        }


class Record(SQLModel, table=True):
    """
    Model of the lead object passed as JSON object in POST request to label_fetch 
    """
    id : Optional[int] = Field(default=None, primary_key=True)
    posted_on : str = None  # None -> same as : null=True
    category : str = None
    skills : str = None
    country : str = None
    message : str = None
    hourly_from : str = None
    hourly_to : str = None
    budget : str = None
    label : str = None
    class Config:
        the_schema = {
            "lead_demo" :{
                "posted_on" : "<p>this is a record</p>",
                "category" : "<p>this is a record</p>",
                "skills" : "<p>this is a record</p>",
                "country" : "<p>this is a record</p>",
                "message" : "<p>this is a record</p>",
                "hourly_from" : "float or empty string",
                "hourly_to" : "float or empty string",
                "budget" : "float or empty string",
                "label" : "empty string",
            }
        }


class MLModel(SQLModel, table=True):
    """
    Model containing ml model name details
    """
    id : Optional[int] = Field(default=None, primary_key=True)
    model_name : str
    model_file : str
    class Config:
        the_schema = {
            "mlmodel_demo" :{
                "model_name" : "jkl_v0",
            }
        }


class MLModelDelete(SQLModel):
    """
    Model Delte Schema
    """
    model_name : str
    class Config:
        the_schema = {
            "mlmodel_delete_demo" :{
                "model_name" : "jkl_v0",
            }
        }


class Users(SQLModel, table=True):
    id : Optional[int] = Field(default=None, primary_key=True)
    fullname : str = Field(default=None)
    email : EmailStr = Field(default=None) # EmailStr is an email validator
    password : str = Field(default=None)
    class Config:
        the_schema = {
            "user_demo" :{
                "fullname" : "abc",
                "email" : "abc@abc.com",
                "password" : "123"
            }
        }


class UserLogin(BaseModel):
    email : EmailStr = Field(default=None) # EmailStr is an email validator
    password : str = Field(default=None)
    class Config:
        the_schema = {
            "user_demo" :{
                "email" : "abc@abc.com",
                "password" : "123"
            }
        }

