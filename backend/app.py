#!/usr/bin/env python3

import redis
import json

from flask import Flask

app = Flask(__name__, static_url_path='', static_folder='static')


redis_db = redis.Redis(decode_responses=True, db=0)


# This function serves to get the video out of our redis DB.
def getvideo() -> object:
    key = redis_db.randomkey()

    if not key:
        app.logger.error('No videos found')
        return {'status': False, 'msg': 'No video'}

    stream = json.loads(key)
    stream['status'] = True
    stream['fetched'] = redis_db.get(key)  # Gets the video object the scrapper saved.
    stream['ttl'] = redis_db.ttl(key)  # This gets the time left before expiration.
    return stream


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/video')
def get() -> object:
    return getvideo()


if __name__ == '__main__':
    app.run()
