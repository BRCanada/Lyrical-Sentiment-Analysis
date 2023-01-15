#-------------SPOTIPY API SCRIPT---------
#  A script written as a container for initial Spotipy API class
#  and request chains to be used in this project.
#
#----------------------------------------

# Import Libraries
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import base64
import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm
#------------------

#-----Spotipy Class Object--------
class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_has_expired = True
    client_id = None
    client_secret = None
    token_url = 'https://accounts.spotify.com/api/token'
    
    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
    
    def get_client_credentials(self):
        """ Returns a base64 encoded string """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("You must set BOTH client_id and client_secret. One or both are currently None type.")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        
        return client_creds_b64.decode()
    
    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }
    
    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        }
    
    def get_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200,299):
            return False
        
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in'] # seconds
        expires = now + datetime.timedelta(seconds=expires_in)
        
        #Update self variables
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_has_expired = expires < now
        return True
    
#------------------------

#---------Spotipy Requests------------

def get_json(url, spotify):
    
    """
    This function returns a json file of a request.
    
    url = String
    spotify = Instantiated SpotifyAPI object
    """
    
    url = url
    access_token = spotify.access_token
    
    # Check access token status, reinitialize if time has expired
    if spotify.access_token_has_expired:
        spotify.get_auth()
        access_token = spotify.access_token

    # Assign token to request header
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Requests chain
    req = requests.get(url, headers=headers)
    print("Status Code: ", req.status_code)     # Status Code
    
    return req.json()