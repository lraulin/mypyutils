# Take 3. Back to how I started in a lot of ways. Except now it's basically
# a front-end for Google tasks and calendar.
from apiclient.discovery import build
from collections import deque
from copy import deepcopy
from dateutil import parser
from httplib2 import Http
from inspect import currentframe, getframeinfo
from math import floor
from oauth2client import file, client, tools
from operator import attrgetter
from os import path
from pathlib import Path
from quickstart import get_events, save_event, save_g_task
from sys import stdout, argv, exit
from time import time, sleep
import argparse
import datetime
import json
import jsonpickle
import pprint
import pyperclip
import pyrebase
import re
import secrets
import shelve
import time

FILENAME = getframeinfo(currentframe()).filename
PARENT = Path(FILENAME).resolve().parent
CREDENTIALS = PARENT / 'credentials.json'
CLIENT_SECRET = PARENT / 'client_secret.json'
DATA_FILE = PARENT / 'pygtd.json'
LIST_IDS_FILE = PARENT / 'g_list_ids.json'
SCOPES = ['https://www.googleapis.com/auth/tasks',
          'https://www.googleapis.com/auth/calendar']

# Set up Google API
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)

with open(LIST_IDS_FILE, 'r') as f:
    LIST_IDS = json.load(f)


def tz_offset():
    """Return local UTC/GMT timezone offset string.

    Format suitable for use in ISO datetime string. Ie -04:00, +09:00.

    """
    ts = time.time()
    seconds = (datetime.datetime.fromtimestamp(ts) -
               datetime.datetime.utcfromtimestamp(ts)).total_seconds()
    hours = round(seconds / (60*60))
    gmt_off = f'{hours:+03}:00'
    return gmt_off


def pythonize(s):
    """Output string in lowercase separated by underscores.

    Ie Hello World => hello_world

    """
    return s.lower().replace(' ', '_')


def get_events(num):
    """Get events from Google Calendar API.

    Returns num number of future events as a list of dictionaries.
    """

    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' = UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=num, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    with open('gcal_test.json', 'w') as f:
        json.dump(events, f)

    return events


def save_event(start, end, summary):
    """Create event in Google Calendar.

    start and end can be either datetime objects or strings.
    """

    cal = build('calendar', 'v3', http=creds.authorize(Http()))

    # Get start and end times in ISO format with UTC offset, whether given as
    # strings or as datetime objects.
    try:
        start = start.isoformat() + tz_offset()
    except AttributeError as e:
        start = parser.parse(start).isoformat() + tz_offset()
    try:
        end = end.isoformat() + tz_offset()
    except AttributeError as e:
        end = parser.parse(end).isoformat() + tz_offset()

    event = {
        'summary': summary,
        'start': {'dateTime': start},
        'end': {'dateTime': end},
    }

    # Create event with Google Calendar API
    e = cal.events().insert(calendarId='primary',
                            sendNotifications=True, body=event).execute()

    # Confirm success
    print('''*** %r event added:
        Start: %s
        End:   %s''' % (e['summary'].encode('utf-8'),
                        e['start']['dateTime'], e['end']['dateTime']))
    return e


def get_tasks():

    service = build('tasks', 'v1', http=creds.authorize(Http()))

    # Call the Tasks API -- get task lists
    lists = {}
    results = service.tasklists().list().execute()
    items = results.get('items', [])
    if not items:
        print('No task lists found.')
    else:
        print('Task lists:')
        for item in items:
            print('{0} ({1})'.format(item['title'], item['id']))
            lists[pythonize(item['title'])] = item['id']

    with open(LIST_IDS_FILE, 'w') as f:
        json.dump(lists, f)

    task_results = service.tasks().list(
        tasklist=list_id, showCompleted=False).execute()
    tasks = task_results.get('items', [])


def save_g_task(item, list):
    print('HEY!')
    # Setup the Tasks API
    service = build('tasks', 'v1', http=creds.authorize(Http()))

    print(LIST_IDS[list])
    service.tasks().insert(
        tasklist=LIST_IDS[list], body=item).execute()


def clear_g_list(list):
    """!!!DELETES ALL CONTENTS OF LIST!!!"""

    # Initialize service
    service = build('tasks', 'v1', http=creds.authorize(Http()))
    # Get list of ids
    task_results = service.tasks().list(
        tasklist=LIST_IDS[list], showCompleted=False).execute()
    tasks = task_results.get('items', [])
    with open('google_tasks_test.json', 'w') as f:
        json.dump(tasks, f)
    ids = [x['id'] for x in tasks]
    for taskID in ids:
        service.tasks().delete(tasklist=LIST_IDS[list], task=taskID).execute()


def main():
    pass


if __name__ == '__main__':
    main()
