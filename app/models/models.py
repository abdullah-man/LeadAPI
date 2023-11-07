from pydantic import BaseModel, Field, EmailStr


class Lead(BaseModel):
    """
    Model of the lead object passed as JSON object in POST request to label_fetch 
    """
    lead : str
    db_model_name : str
    class Config:
        the_schema = {
            "lead_demo" :{
                "lead" : "<p>this is a lead</p>",
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

