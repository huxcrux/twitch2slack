#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Docstring """

import time
import json
import logging
import requests
from dateutil import parser
from pytz import timezone
from twitchchannelquery import twitchchannelquery

# pylint: disable=invalid-name,global-statement

CONFIG_FILE = "config.json"
SAVE_CONFIG = True
stream_online = False
stream_online_seconds = 0
stream_views = 0
stream_followers = 0
stream_start_views = 0
stream_start_followers = 0

def save_config(f, cfg):
    """ Save JSON-formatted file """
    try:
        with open(f, 'w') as configfile:
            json.dump(cfg, configfile, indent=4)
    except:
        return False
    return True

def read_config(f):
    """ Read JSON-formatted file """
    data = []
    try:
        with open(f, 'r') as configfile:
            data = json.load(configfile)
    except (FileNotFoundError, PermissionError):
        pass
    return data

def default_config():
    """ Return default json-formatted config """
    return {"channel": "https://api.twitch.tv/kraken/streams/LuppiiMC", "webhook": "", \
        "username": "twitch", "tz": "Europe/Stockholm", "fmt": "%Y-%m-%d %H:%M:%S %Z%z", \
        "slack-channel": "#webhook-test"}

def iso8601_to_epoch(iso8601):
    """ Converts ISO 8601 datetime format to epoch """
    return parser.parse(iso8601).strftime('%s')

def online_seconds(start):
    """ Calculate  """
    now = time.mktime(time.gmtime())
    return int(now-start)

def generate_message(channel):
    """ Docstring """
    global stream_online
    global stream_online_seconds
    global stream_start_views
    global stream_start_followers
    global stream_views
    global stream_followers

    if channel.is_online() and not stream_online:
        stream_online = True
        stream_views = channel.get_views()
        stream_followers = channel.get_followers()
        stream_start_views = channel.get_views()
        stream_start_followers = channel.get_followers()
        stream_online_seconds = online_seconds(float(iso8601_to_epoch(channel.get_start_time())))
        start_time_formatted = parser.parse(channel.get_start_time()).astimezone(timezone(CONFIG["tz"])).strftime(CONFIG["fmt"])

        print("Channel is online.")
        print("Stream ID:", channel.get_stream_id())
        print("Start time:", start_time_formatted)
        print("Online time: %dh:%02dm:%02ds" % (stream_online_seconds // 3600, \
            stream_online_seconds % 3600 // 60, stream_online_seconds % 60))
        print("Game:", channel.get_game())
        print("Title:", channel.get_status())
        print("Total views:", channel.get_views())
        print("Followers:", channel.get_followers())

        message = "Stream is live! <%s|Stream link>\nStream ID: %d\nStart time: %s\nGame: %s\nTitle: %s" \
            % (channel.get_stream_url(), channel.get_stream_id(), start_time_formatted, channel.get_game(), channel.get_status())

        if CONFIG["webhook"]:
            send_message(CONFIG["webhook"], CONFIG["username"], CONFIG["slack-channel"], message)
    elif channel.is_online() and stream_online:
        stream_views = channel.get_views()
        stream_followers = channel.get_followers()
        stream_online_seconds = online_seconds(float(iso8601_to_epoch(channel.get_start_time())))
        print("Stream is still online. Updating stats.")
    elif not channel.is_online() and stream_online:
        stream_online = False
        message = "Stream is now offline.\nOnline time: %dh %02dm\nViews: %d (%d)\nFollowers: %d (%d)" \
            % (stream_online_seconds // 3600, stream_online_seconds % 3600 // 60, \
            stream_views, stream_views - stream_start_views, stream_followers, \
            stream_followers - stream_start_followers)
        stream_online_seconds = 0
        stream_views = 0
        stream_followers = 0
        stream_start_views = 0
        stream_start_followers = 0

        print(message)
        if CONFIG["webhook"]:
            send_message(CONFIG["webhook"], CONFIG["username"], CONFIG["slack-channel"], message)
    else:
        print("Channel \"" + CONFIG["channel"].split('/')[-1] + "\" is offline.")

def send_message(url, username, channel, string):
    """ Docstring """
    payload = {"username": username, "channel": channel, "text": string}
    requests.post(url, json=payload)


logging.getLogger("requests").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO,
                    filename='twitchq.log',
                    format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

CONFIG = read_config(CONFIG_FILE)
if not CONFIG:
    CONFIG = default_config()
    if SAVE_CONFIG is True:
        save_config(CONFIG_FILE, CONFIG)

channel = twitchchannelquery()
channel.setup(CONFIG["channel"])

logging.info("Service is started.")
print("Querying channel every 60 seconds. Press 'Ctrl + C' to interrupt.\n\n")
try:
    while True:
        channel.query()
        generate_message(channel)
        channel.reset()
        time.sleep(60)
except (SystemExit, KeyboardInterrupt):
    logger.info("Service is stopping.")
    print("\nExiting.")
except Exception as e:
    logger.error("Something bad happened", exc_info=True)

logger.info("Service is stopped.")
