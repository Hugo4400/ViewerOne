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

REQUEST_LIMIT = 1500  # Number of API requests to run
MINIMUM_VIDEOS_TO_GET = 50  # The number of videos to get, unless limit is hit.
SECONDS_BEFORE_RECORD_EXPIRATION = 180  # How many seconds a video should stay in redis.

main_redis = redis.Redis(decode_responses=True, db=0)

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
random = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3))

youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)

requests_sent = 0
videos_grabbed = 0
while requests_sent <= REQUEST_LIMIT or videos_grabbed < MINIMUM_VIDEOS_TO_GET:
    request = youtube.search().list(
        type='video',
        q=random,
        maxResults=50,
        part='snippet'
    )
    requests_sent += 1

    searchResponse = request.execute()

    for videos in searchResponse['items']:
        req = youtube.videos().list(
            part='statistics',
            id=videos['id']['videoId']
        )
        requests_sent += 1

        res = req.execute()

        for video in res['items']:
            if int(video['statistics']['viewCount']) <= 0:
                videos_grabbed += 1
                main_redis.setex(json.dumps(video), SECONDS_BEFORE_RECORD_EXPIRATION, time.time())

