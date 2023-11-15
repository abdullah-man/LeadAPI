import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.routes import routes_router
from app.database.connection import conn

app = FastAPI()

# Register origins - Allow all origins : * 
# actually only axiom odoo server will be allowed to access the api
# origins = ["https://hq.axm.app/"]
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(routes_router)

@app.on_event("startup")
def on_startup():
    conn()


if __name__== '__main__':
    uvicorn.run("application:app", host="127.0.0.1", port=8000, reload=True)
