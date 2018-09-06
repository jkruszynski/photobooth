import requests
import logging


class GetToken:
    def __init__(self, config):
        """ Uses google oauth credentials to refresh token to use for uploading every 30 mins"""

        self.url = "https://accounts.google.com/o/oauth2/token"
        self.client_id = config.get('OAuth', 'client_id')
        self.client_secret = config.get('OAuth', 'client_secret')
        self.redirect_uri = config.get('OAuth', 'redirect_uri')
        self.refresh_token = config.get('OAuth', 'refresh_token')

        self.payload = "grant_type=refresh_token&client_id=" + self.client_id + "&client_secret=" \
                       + self.client_secret + "&redirect_uri=" + self.redirect_uri + "&refresh_token=" \
                       + self.refresh_token
        self.headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache"
        }

        self.response = requests.request("POST", self.url, data=self.payload, headers=self.headers)
        if 'access_token' in self.response.json().keys():
            token = self.response.json()['access_token']
            with open('token.txt', 'w') as f:
                f.write(token)
        else:
            logging.error('invalid values')
