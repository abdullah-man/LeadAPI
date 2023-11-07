"""
Simulates a Client for REST API
"""

import requests
import pandas as pd
import json


def get_data() -> None:
    """
    Simulates a client sending request to get data from Rest API and saves it in an Excel file
    """
    response = requests.get('http://127.0.0.1:8000/data_fetch')

    # response dictionary
    response_dict = json.loads(response.text)

    # for i in response_dict:
    #     print("key: ", i, "val: ", response_dict[i])

    # cols = columns=['posted_on', 'category', 'skills', 'country', 'message', 'hourly_from', 'hourly_to', 'budget', 'label', 'id']
    data = pd.DataFrame(response_dict)
    print(data.columns)
    data.to_excel("fetched.xlsx", index=False)


def get_labeled_extracted_data(rss_feed) -> object:
    """
    Sends a json object containing raw lead rss feed to Rest API,
    receives a json object containing extracted info and label
    parameters:
        rss_feed: dict object
    returns:
        JSON object
    """
    response = requests.post('http://127.0.0.1:8000/label_fetch', json=rss_feed) # json parameter takes a dict
    # response dictionary - extract data from response
    response_dict = response.json()
    return response_dict


def delete_model(model_details) -> None:
    """
    Deletes a ML Model from database and server 
    """
    response = requests.post('http://127.0.0.1:8000/model_delete', json=model_details) # json parameter takes a dict
    # response dictionary - extract data from response
    response_dict = response.json()
    return response_dict


# ------------------------

# sign-up
sign_up_response = requests.post('http://127.0.0.1:8000/user/signup',
                                 headers={'accept' : 'application/json', 'Content-Type' : 'application/json'},
                                 json={"fullname": "abd", "email": "abd@example.com", "password": "string"})
signup_response_dict = json.loads(sign_up_response.text)

# login
log_in_response = requests.post('http://127.0.0.1:8000/user/login',
                                headers={'accept' : 'application/json', 'Content-Type' : 'application/json'},
                                json={"email": "abd@example.com", "password": "string"})

login_response_dict = json.loads(log_in_response.text)

# label_fetch - a Lead for inference
rss_feed = """"<p>I need an odoo expert to assist with importing data and setting up a new odoo application for an existing business we've just aquired.<br> 
# We will be importing data from MailChimp, Xero, WordPress and WooCommerce, setting up inventory, email templates, automations and campaigns and other work as needed.<br> 
# The bulk of this work will take place over the next few weeks, but I suspect there will be ongoing work for the right candidate. <br><br><b>Hourly Range</b>: $7.00-$20.00 
 
# <br><b>Posted On</b>: August 06, 2023 09:40 UTC<br><b>Category</b>: Full Stack Development<br><b>Skills</b>:Odoo     
# <br><b>Country</b>: Australia 
# <br><a href=""https://www.upwork.com/jobs/Odoo-Expert_%7E01a4aae9e53e923117?source=rss"">click to apply</a> 
# <br> 
# <br> 
# from All jobs | <a href=""http://upwork.com"">upwork.com</a> <a href=""https://ift.tt/pWj7omN"">https://ift.tt/pWj7omN</a><br> 
# via <a href=""https://ifttt.com/?ref=da&amp;site=gmail"">IFTTT</a> 
# </p>"""

rss_feed = {'lead' : rss_feed, 'db_model_name' : 'rf_clf_v0'}
bearer_token = login_response_dict['access token']
print(bearer_token)
post_response = requests.post('http://127.0.0.1:8000/label_fetch',
                              headers={'accept' : 'application/json', 'Content-Type' : 'application/json', 'Authorization' : f'Bearer {bearer_token}'},
                              json=rss_feed)

post_response_dict = json.loads(post_response.text)
print(post_response_dict)


# ------------------------

# upload a trained model
# model = "../Pipeline/rf_clf_v0.1.model"
# send_model()

# get data from warehouse
# get_data()

# get labeled extracted data
# rss_feed = """"<p>I need an odoo expert to assist with importing data and setting up a new odoo application for an existing business we've just aquired.<br> 
# # We will be importing data from MailChimp, Xero, WordPress and WooCommerce, setting up inventory, email templates, automations and campaigns and other work as needed.<br> 
# # The bulk of this work will take place over the next few weeks, but I suspect there will be ongoing work for the right candidate. <br><br><b>Hourly Range</b>: $7.00-$20.00 
 
# # <br><b>Posted On</b>: August 06, 2023 09:40 UTC<br><b>Category</b>: Full Stack Development<br><b>Skills</b>:Odoo     
# # <br><b>Country</b>: Australia 
# # <br><a href=""https://www.upwork.com/jobs/Odoo-Expert_%7E01a4aae9e53e923117?source=rss"">click to apply</a> 
# # <br> 
# # <br> 
# # from All jobs | <a href=""http://upwork.com"">upwork.com</a> <a href=""https://ift.tt/pWj7omN"">https://ift.tt/pWj7omN</a><br> 
# # via <a href=""https://ifttt.com/?ref=da&amp;site=gmail"">IFTTT</a> 
# # </p>"""
# rss_feed = {'lead' : rss_feed, 'db_model_name' : 'rf_clf_v0'}

# data = get_labeled_extracted_data(rss_feed=rss_feed)
# print(data)


