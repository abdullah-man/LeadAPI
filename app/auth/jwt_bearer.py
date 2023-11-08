# contains code to extract and parse token from http authorization header
# Code to check if the request is authorized or not - based on this it is given access to
# the endpoint/route

from typing import Optional
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt_handler import decodeJWT


class jwtBearer(HTTPBearer):
    """Used to persist authenticaiton on the routes
    """
    # calling super, to make its everything accessible in jwtBearer objects
    def __init__(self, auto_error: bool = True):
        super(jwtBearer, self).__init__(auto_error=auto_error)
    
    #to get the credentials of the Bearer of the token
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        # funciton overriding of __call__ method of parent class
        # this simply calls the __call__ method of the super class 
        # this may take time, hence : await
        credentials : HTTPAuthorizationCredentials = await super(jwtBearer, self).__call__(request)
        
        # check if the credentials scheme is not a Bearer scheme
        if credentials:
            if not credentials.scheme == 'Bearer': 
                # then we would raise an exception
                raise HTTPException(status_code= 403, detail="Invalid token or expired token")
            # verifying validity of the token by checking its expiry time
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")

            return credentials.credentials
        else:
            raise HTTPException(status_code= 403, detail="Invalid/Expired token")


    def verify_jwt(self, jwtoken : str):   
        # to check if a jwt token is valid or not
        isTokenValid : bool = False        
        try:
            payload = decodeJWT(jwtoken) # decode the token - returns True or False
        except:
            payload = None
        
        if payload:
                isTokenValid = True
            
        return isTokenValid
        

    




 
