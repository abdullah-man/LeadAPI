from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool  
import pytest
import json

from app.database.connection import get_session
from application import app
from app.models.models import Record

# 1 ---- test database and session creation using pytest fixtures to reduce boilerplate code ----
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")  
def client_fixture(session: Session):  
    def get_session_override():  
        return session
    
    app.dependency_overrides[get_session] = get_session_override  
    client = TestClient(app)  
    yield client  
    app.dependency_overrides.clear()  


# 2 ---- Unit tests ----

# check server running
def test_server_running(client : TestClient):
    response = client.get("/docs")
    assert response.status_code == 200

def test_data_fetch(session : Session, client : TestClient):
    bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySUQiOiJhYmRAZXhhbXBsZS5jb20iLCJleHBpcmVzIjoxNzMxNDg0Mzk2LjUxMTA4Nn0.S0rLV-AJKRUtzuI6A-Enf_hxxAtnYLZu8MkEwiootxg"
    response = client.get('http://127.0.0.1:8000/data_fetch',
                                  headers={'accept' : 'application/json', 'Content-Type' : 'application/json', 'Authorization' : f'Bearer {bearer_token}'},)
    
    data = json.loads(response.text)

    assert response.status_code == 200
    assert isinstance(data, list)
    for instance in data:
        assert isinstance(instance, Record)

def test_model_upload(session : Session, client : TestClient):
    pass

def test_label_fetch(session : Session, client : TestClient):
    bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySUQiOiJhYmRAZXhhbXBsZS5jb20iLCJleHBpcmVzIjoxNzMxNDg0Mzk2LjUxMTA4Nn0.S0rLV-AJKRUtzuI6A-Enf_hxxAtnYLZu8MkEwiootxg"
    rss_feed = {'posted_on': 'August 06, 2023 09:40 UTC', 'category': 'Full Stack Development', 'skills': 'Odoo', 'country': 'Australia', 'message': '"I need an odoo expert to assist with importing data and setting up a new odoo application for an existing business we\'ve just aquired. # We will be importing data from MailChimp, Xero, WordPress and WooCommerce, setting up inventory, email templates, automations and campaigns and other work as needed. # The bulk of this work will take place over the next few weeks, but I suspect there will be ongoing work for the right candidate.', 'hourly_from': 7.0, 'hourly_to': 20.0, 'budget': '', 'model_name' : 'rf_clf_v0'}
    response = client.post('http://127.0.0.1:8000/label_fetch',
                              headers={'accept' : 'application/json', 'Content-Type' : 'application/json', 'Authorization' : f'Bearer {bearer_token}'},
                              json=rss_feed)

    data = json.loads(response.text)
    assert response.status_code == 200
    assert isinstance(data, str)
    assert data=='Applied' or data=='Rejected'
    

def test_model_delete(session : Session, client : TestClient):
    pass

def test_signup(session : Session, client : TestClient):
    pass

def test_login(session : Session, client : TestClient):
    pass

def test_token_expired(session : Session, client : TestClient):
    pass

def test_user_already_exists(session : Session, client : TestClient):
    pass
