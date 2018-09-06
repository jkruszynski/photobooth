import requests
import json
import logging


class UploadPhoto:
    def __init__(self, config, pic):
        """ Uploading is 2 part process. You first upload a media item onto the Google Server.
            Next, you move that media item to your google photo """

        logging.info('Starting upload of ' + pic)
        self.album_id = 'ANIRYEinV8at4ihMSNqxJOrpBWfkKxrnlh3TAl0YYGYDIffZJ0JUK1jj82C-okNW8oyna0jhtl48'
        self.album_id = config.get('OAuth', 'album_id')

        self.token= ''
        with open('token.txt','r') as f:
            self.token = f.read()

        self.url = "https://photoslibrary.googleapis.com/v1/uploads"

        self.headers = {
            'Content-type': "application/octet-stream",
            'X-Goog-Upload-Protocol': "raw",
            'Authorization': "Bearer " + self.token,
            'Cache-Control': "no-cache"
            }

        self.response = requests.request("POST", self.url, headers=self.headers, data=open(pic, 'rb').read())

        self.upload_token = self.response.text

        self.url = "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate"

        self.payload = {
            "albumId": self.album_id,
          "newMediaItems": [
            {
              "description": "testing",
              "simpleMediaItem": {
                "uploadToken": self.upload_token
              }
            }
          ]
        }
        self.headers = {
            'Content-Type': "application/json",
            'Authorization': "Bearer " + self.token,
            'Cache-Control': "no-cache"
            }

        self.response = requests.request("POST", self.url, data=json.dumps(self.payload), headers=self.headers)
        logging.info('Finished upload of ' + pic)