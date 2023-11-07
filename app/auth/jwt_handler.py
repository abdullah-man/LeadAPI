# responsible for signing, encoding, decoding, returning of the tokens
import time # to set expiray of the token
import datetime
import jwt # for encoding and decoding of the generated token strings
from decouple import config # helps in organizing our settings, so that we can
                            # change parameters without having to redeploy the application

# get variables from .env file
JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


def token_respose(token : str):
    """Returns a JWT token encoded as a string from a dictionary body/payload
    """
    return {
        "access token" : token
    }


def signJWT(userID : str): # userID is username/email of the user
    """To sign the JWt string
    """
    # a dict containing userID and expiration time
    payload = {
        "userID" : userID,
        "expiry" : (datetime.datetime.utcnow() + datetime.timedelta(365)).timestamp() # 365 days validity
    }
    # now creating the token
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)  
    return token_respose(token=token)


def decodeJWT(token : str):
    """Takes a token and decodes it using jwt package, and if expiratio date is valid,
    return the token 
    """
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decode_token if decode_token['expires'] >= (datetime.datetime.utcnow()).timestamp() else None 
    except:
        return {} 