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
SCOPES = 'https://www.googleapis.com/auth/calendar'


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


def get_events(num):
    """Get events from Google Calendar API.

    Returns num number of future events as a list of dictionaries.
    """

    # Setup the Calendar API

    store = file.Storage(CREDENTIALS)
    creds = store.get()
    if not creds or creds.invalid:
        print('Not creds or creds invalid!')
        flow = client.flow_from_clientsecrets(CLIENT_SECRET, SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
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

    # Setup the Calendar API
    store = file.Storage(CREDENTIALS)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET, SCOPES)
        creds = tools.run_flow(flow, store)
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


def main():
    pass


if __name__ == '__main__':
    main()
