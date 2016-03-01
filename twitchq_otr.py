#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Docstring """

import json
import time
import requests
from dateutil import parser
from pytz import timezone
from twitchchannelquery import twitchchannelquery

# pylint: disable=invalid-name,global-statement

CONFIG_FILE = "config.json"
STREAM_FILE = "stream.json"
SAVE_CONFIG = True
TRIES = 3

def save_json(f, cfg):
    """ Save JSON-formatted file """
    try:
        with open(f, 'w') as configfile:
            json.dump(cfg, configfile, indent=4)
    except:
        return False
    return True

def read_json(f):
    """ Read JSON-formatted file """
    data = []
    try:
        with open(f, 'r') as configfile:
            data = json.load(configfile)
    except (FileNotFoundError, PermissionError):
        pass
    return data

def default_json(flag):
    """ Return default json

        Flags:
        * config: Return default config set
        * stream: Return default stream set
    """
    if flag is 'config':
        return {"channel": "https://api.twitch.tv/kraken/streams/LuppiiMC", "webhook": "", \
            "username": "twitch", "tz": "Europe/Stockholm", "fmt": "%Y-%m-%d %H:%M:%S %Z%z", \
            "slack-channel": "#webhook-test"}
    elif flag is 'stream':
        return {"online": False, "sid": "", "start_time": "", "start_views": 0, "start_followers": 0, "views": 0, "followers": 0}
    else:
        return {}

def iso8601_to_epoch(iso8601):
    """ Converts ISO 8601 datetime format to epoch """
    return parser.parse(iso8601).strftime('%s')

def online_seconds(start):
    """ Calculate  """
    now = time.mktime(time.gmtime())
    return int(now-start)

def generate_message(channel, stream, f):
    """ Docstring """
    if channel.is_online() and stream["sid"] and (channel.get_stream_id() != stream["sid"]):
        stream = reset(stream)

    if channel.is_online() and not stream["online"]:
        stream["online"] = True
        stream["sid"] = channel.get_stream_id()
        stream["views"] = channel.get_views()
        stream["followers"] = channel.get_followers()
        stream["start_views"] = channel.get_views()
        stream["start_followers"] = channel.get_followers()
        stream["start_time"] = channel.get_start_time()
        stream_online_seconds = online_seconds(float(iso8601_to_epoch(stream["start_time"])))
        start_time_formatted = parser.parse(stream["start_time"]).astimezone(timezone(CONFIG["tz"])).strftime(CONFIG["fmt"])

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
            % (channel.get_stream_url(), stream["sid"], start_time_formatted, channel.get_game(), \
            channel.get_status())

        save_json(f, stream)

        if CONFIG["webhook"]:
            send_message(CONFIG["webhook"], CONFIG["username"], CONFIG["slack-channel"], message)
    elif channel.is_online() and stream["online"]:
        stream["views"] = channel.get_views()
        stream["followers"] = channel.get_followers()
        save_json(f, stream)
        print("Stream is still online. Updating stats.")
    elif not channel.is_online() and stream["online"]:
        stream = reset(stream)
    else:
        print("Channel \"" + CONFIG["channel"].split('/')[-1] + "\" is offline.")

def reset(stream):
    stream_online_seconds = online_seconds(float(iso8601_to_epoch(stream["start_time"])))
    message = "Stream is now offline.\nOnline time: %dh %02dm\nViews: %d (%d)\nFollowers: %d (%d)" \
        % (stream_online_seconds // 3600, stream_online_seconds % 3600 // 60, \
        stream["views"], stream["views"] - stream["start_views"], stream["followers"], \
        stream["followers"] - stream["start_followers"])

    stream = default_json('stream')
    save_json(STREAM_FILE, stream)

    print(message)
    if CONFIG["webhook"]:
        send_message(CONFIG["webhook"], CONFIG["username"], CONFIG["slack-channel"], message)
    return stream

def send_message(url, username, channel, string):
    """ Docstring """
    payload = {"username": username, "channel": channel, "text": string}
    requests.post(url, json=payload)


CONFIG = read_json(CONFIG_FILE)
if not CONFIG:
    CONFIG = default_json('config')
    if SAVE_CONFIG is True:
        save_json(CONFIG_FILE, CONFIG)
stream = read_json(STREAM_FILE)
if not stream:
    stream = default_json('stream')

channel = twitchchannelquery()
channel.setup(CONFIG["channel"])
num_tries = 0
while num_tries < TRIES:
    channel.query()
    if channel.is_online:
        num_tries = 3
    if not channel.is_online and not stream["online"]:
        num_tries = 3
    num_tries += 1
generate_message(channel, stream, STREAM_FILE)

