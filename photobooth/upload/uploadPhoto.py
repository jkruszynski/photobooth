import requests
import json
import logging


class UploadPhoto:
    def run(config, pic):
        """ Uploading is 2 part process. You first upload a media item onto the Google Server.
            Next, you move that media item to your google photo """

        logging.info('Starting upload of ' + pic)

        album_id = config.get('OAuth', 'album_id')

        token= ''
        with open('token.txt','r') as f:
            token = f.read()

        url = "https://photoslibrary.googleapis.com/v1/uploads"

        headers = {
            'Content-type': "application/octet-stream",
            'X-Goog-Upload-Protocol': "raw",
            'Authorization': "Bearer " + token,
            'Cache-Control': "no-cache"
            }
        try:
            response = requests.request("POST", url, headers=headers, data=open(pic, 'rb').read())
        except:
            return False

        upload_token = response.text

        url = "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate"

        payload = {
            "albumId": album_id,
          "newMediaItems": [
            {
              "description": "testing",
              "simpleMediaItem": {
                "uploadToken": upload_token
              }
            }
          ]
        }
        headers = {
            'Content-Type': "application/json",
            'Authorization': "Bearer " + token,
            'Cache-Control': "no-cache"
            }


        try:
            response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
        except:
            return False
        print(response.text)

        logging.info('Finished upload of ' + pic)
        try:
            if response.json()['newMediaItemResults'][0]['status']['message'] == 'OK':
                return True
        except:
            return False

