from pydantic import BaseModel, Field, EmailStr
from typing import Union


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
    db_model_name : str
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
                "label" : "empty string",
                "db_model_name" : "jkl_v0",
            }
        }


class ModelDetails(BaseModel):
    """
    Model containing ml model name details
    """
    db_model_name : str
    class Config:
        the_schema = {
            "mlmodel_demo" :{
                "db_model_name" : "jkl_v0",
            }
        }


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

