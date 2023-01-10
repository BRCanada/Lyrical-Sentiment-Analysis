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

#-------Spotipy Playlist Request Chain -------
def api_to_csv(url, spotify):
    
    """
    Function designed to make an initial playlist request to Spotify Web API, iterating through every page and appending key features to one dataframe. Write final dataframe to csv in "../data/<file.csv>"
    
    url = String
    spotify = Instantiated SpotifyAPI object
    """
    
    url = url
    page_trigger = True
    access_token = spotify.access_token
    df = pd.DataFrame(columns=['track_name', 'artist', 'album', 'track_url', 'preview_url'])
    
    while page_trigger:
        if spotify.access_token_has_expired:
            spotify.get_auth()
            access_token = spotify.access_token
        
        headers = {
                "Authorization": f"Bearer {access_token}"
                }
        
        temp_df = pd.DataFrame()
        req = requests.get(url, headers=headers)
        print("Status Code: ", req.status_code)
        
        json_res = req.json()
        
        data = json_res['items']
        
        for i in range(0, len(data)):
            temp_df.at[i, 'track_name'] = data[i]['track']['name']
            temp_df.at[i, 'artist'] = data[i]['track']['artists'][0]['name']
            temp_df.at[i, 'album'] = data[i]['track']['album']['name']
            temp_df.at[i, 'track_url'] = data[i]['track']['href']
            temp_df.at[i, 'preview_url'] = data[i]['track']['preview_url']
            temp_df.at[i, 'artist_url'] = data[i]['track']['artists'][0]['href']
        
        df = pd.concat([temp_df, df], axis=0)
        
        if type(json_res['next']) == str:
            url = json_res['next']
            page_trigger = True
        else:
            page_trigger = False

    df.to_csv('../data/playlist_data.csv', sep=';', columns=df.columns)
        
#------------------------------------------------

#----------Label Printer Function----------------
def label_printer(feature, spotify):
    """
    This function will apply a request chain to each track and return a Series of lists.
    
    feature = Pandas Series
    spotify = Instantiated SpotifyAPI object
    """
    gen_list = []
    
    for item in tqdm(feature):
        url = item
        
        if spotify.access_token_has_expired:
            spotify.get_auth()
            access_token = spotify.access_token    
            
        headers = {
                "Authorization": f"Bearer {access_token}"
                }
        
        req = requests.get(url, headers=headers)
        output = req.json()
        
        gen_list.append(output['genres'])
    
    return gen_list