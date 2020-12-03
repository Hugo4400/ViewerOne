import os
import json
import logging
import redis
import sys
import time
import random
import string
import googleapiclient.discovery
import googleapiclient.errors

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

API_KEY = os.environ.get('API_KEY')

if not API_KEY:
    logging.error('API_KEY not set correctly! Exiting...')
    exit(1)


def logerror(result) -> None:
    logging.error('Error (' + result['error']['code'] + '): ' + result['error']['message'])


REQUEST_LIMIT = 1500  # Number of API requests to run
MINIMUM_VIDEOS_TO_GET = 100  # The number of videos to get, unless limit is hit.
SECONDS_BEFORE_RECORD_EXPIRATION = 21600  # How many seconds a video should stay in redis.

main_redis = redis.Redis(decode_responses=True, db=0)

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)

requests_sent = 0
videos_grabbed = 0
while requests_sent <= REQUEST_LIMIT or videos_grabbed < MINIMUM_VIDEOS_TO_GET:

    random = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3))
    request = youtube.search().list(
        type='video',
        q=random,
        maxResults=50,
        part='snippet'
    )

    searchResponse = request.execute()
    requests_sent += 1

    if not searchResponse['error']:

        for videos in searchResponse['items']:
            req = youtube.videos().list(
                part='statistics',
                id=videos['id']['videoId']
            )

            res = req.execute()
            requests_sent += 1

            if not res['error']:

                for video in res['items']:
                    if int(video['statistics']['viewCount']) <= 0:
                        videos_grabbed += 1
                        main_redis.setex(json.dumps(video), SECONDS_BEFORE_RECORD_EXPIRATION, time.time())

            else:
                logerror(res)

    else:
        logerror(searchResponse)

