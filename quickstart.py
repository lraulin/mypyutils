# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START calendar_quickstart]
"""
Shows basic usage of the Google Calendar API. Creates a Google Calendar API
service object and outputs a list of the next 10 events on the user's calendar.
"""
# When adding/changing scope, I get an insuffficient permissions error.
# I can make it re-do the authorization by deleting/hiding credentials.json,
# forcing it to ask for authorization and create a new one. Probably not the
# correct way to do it, but it works for now.
#
# Dev console for tasks api:
# https://console.developers.google.com/apis/api/tasks.googleapis.com/overview?project=pygtd-b8b3d&duration=PT1H
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
import json
import time
from dateutil import parser
from inspect import currentframe, getframeinfo
from pathlib import Path

FILENAME = getframeinfo(currentframe()).filename
PARENT = Path(FILENAME).resolve().parent
CREDENTIALS = PARENT / 'credentials.json'
CLIENT_SECRET = PARENT / 'client_secret.json'
LIST_IDS_FILE = PARENT / 'g_list_ids.json'
SCOPES = ['https://www.googleapis.com/auth/tasks',
          'https://www.googleapis.com/auth/calendar']

# Set up Google API
store = file.Storage(CREDENTIALS)
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET, SCOPES)
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


def fetch_g_tasks(bucket):
    """Fetch uncompleted tasks from Google API & return as list of dicts.

    Takes list name as input which is matched with list ID using json file
    to retrieve tasks for that list.
    """

    # Initialize Google API service
    service = build('tasks', 'v1', http=creds.authorize(Http()))

    # Call the Tasks API -- get task lists
    lists = {}
    results = service.tasklists().list().execute()
    items = results.get('items', [])
    if not items:
        print('No task lists found.')
    else:
        for item in items:
            # Reformat list name ('Next Actions' becomes 'next_actions')
            # Use name as key for list id
            lists[pythonize(item['title'])] = item['id']

    # Update tasklist-ID dictionary to make sure it stays current
    with open(LIST_IDS_FILE, 'w') as f:
        json.dump(lists, f)

    # Retrieve tasks for selected list from API
    task_results = service.tasks().list(
        tasklist=LIST_IDS[bucket], showCompleted=False).execute()
    tasks = task_results.get('items', [])
    return tasks


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


def delete_g_task(taskID, list):
    """Delete task from Google tasks."""

    # Initialize service
    service = build('tasks', 'v1', http=creds.authorize(Http()))
    # Delete task
    service.tasks().delete(tasklist=LIST_IDS[list], task=taskID).execute()


def complete_g_task(taskID, list):
    """Mark Google task as completed."""

    # Initialize service
    service = build('tasks', 'v1', http=creds.authorize(Http()))

    # First retrieve the task to update.
    task = service.tasks().get(
        tasklist=LIST_IDS[list], task='taskID').execute()
    task['status'] = 'completed'

    result = service.tasks().update(
        tasklist=LIST_IDS[list], task=task['id'], body=task).execute()
    # Print the completed date.
    print(f"Task completed at {result['completed']}")


def main():
    pass


if __name__ == '__main__':
    main()
