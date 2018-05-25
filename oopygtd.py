#!/usr/bin/env python3

"""
Class-based version for possible refactor. Maybe will use ORM. For now, I think
I'll use shelf for storage.
"""

import argparse
import json
import pyperclip
import datetime
import re
import shelve
import jsonpickle
from os import path
from time import time, sleep
from sys import stdout, argv, exit
from dateutil import parser
from inspect import currentframe, getframeinfo
from pathlib import Path
from operator import attrgetter
from collections import OrderedDict

FILENAME = getframeinfo(currentframe()).filename
PARENT = Path(FILENAME).resolve().parent
DATA_FILE = PARENT / 'pygtd.json'
PICKLE_FILE = PARENT / 'pickle.json'


def timedif(then):
    """Returns time difference between now and Unix timestamp."""
    difsec = time() - then
    return round(difsec)


class Item:
    id_count = 0

    def __init__(self):
        self.__class__.id_count += 1
        self.id = self.__class__.id_count
        self.created = time()
        self.completed = None

    def age(self):
        return timedif(self.created)


class InboxItem(Item):
    def __init__(self, text):
        Item.__init__(self)
        self.text = text


class Inbox():
    def __init__(self, items=[]):
        self.items = items

    def add(self, text):
        item = InboxItem(text)
        self.items.append(item)

    def print(self):
        for item in self.items:
            print(str(item.id) + ' ' + item.text)


class NextAction(Item):
    def __init__(self, text, context=None):
        Item.__init__(self)
        self.created = time()
        self.text = text
        self.context = context


class NextActionList():
    def __init__(self, items=[]):
        self.items = items

    def print(self):
        for item in self.items:
            print(str(item.id), item.text)


class WaitingFor(Item):
    def __init__(self, text, agent='', due=None):
        Item.__init__(self)
        self.created = time()
        self.agent = agent
        self.text = text
        self.due = due


class WaitingForList():
    def __init__(self, items=[]):
        self.items = items


class Project(Item):
    def __init__(self, text):
        Item.__init__(self)
        self.text = text


class ProjectList():
    def __init__(self, items):
        self.items = items


class MaybeSomeday(Item):
    def __init__(self, text, category=''):
        Item.__init__(self)
        self.text = text
        self.category = category


class MaybeSomedayList():
    def __init__(self, items=[]):
        self.items = items


class CalendarItem(Item):
    def __init__(self, date, text):
        Item.__init__(self)
        self.date = date
        self.text = text


class Calendar():
    def __init__(self, items=[]):
        self.items = items

    def add(self, item):
        self.items.append(item)

    def print_upcoming(self, days=30):
        today = datetime.datetime.today()
        self.items.sort(key=attrgetter('date'))
        for item in self.items:
            date = item.date.strftime('%a, %b %d')
            time = item.date.strftime('%I:%M%p')
            if not time == '12:00AM':
                date += ' ' + time
            delta = item.date - today
            days = delta.days
            hours = round(delta.seconds / 3600)
            print('{}: {} ({} days, {} hours)'.format(
                date,
                item.text,
                days,
                hours
            ))
        # TODO: test if date is within days or less in the future


class CompletedItemList():
    def __init__(self, items=[]):
        self.items = items


d = {
    'inbox': Inbox(),
    'calendar': Calendar(),
    'next_actions': NextActionList(),
    'waiting_for': WaitingForList(),
    'maybe_someday': MaybeSomedayList(),
    'completed_items': CompletedItemList()
}


def import_json():
    global d
    with open(DATA_FILE, 'r') as file:
        data = json.load(file)

    # Import Inbox
    for key, value in data['inbox'].items():
        newitem = InboxItem(value)
        newitem.created = key
        d['inbox'].items.append(newitem)

    # Import Next Actions
    for key, value in data['actions'].items():
        newitem = NextAction(value)
        newitem.created = key
        d['next_actions'].items.append(newitem)

    # Import Calendar
    for key, value in data['scheduled'].items():
        date = parser.parse(value['date'])
        newitem = CalendarItem(date, value['text'])
        newitem.created = key
        d['calendar'].add(newitem)

    # Import Waiting For
    for key, value in data['waiting'].items():
        newitem = WaitingFor(value)
        newitem.created = key
        d['waiting_for'].items.append(newitem)

    # Import Completed Items
    for key, value in data['completed'].items():
        newitem = NextAction(value['text'])
        newitem.created = key
        newitem.completed = value['completion_date']
        d['completed_items'].items.append(newitem)

    test = ''
    with shelve.open('pygtdshelf') as file:
        test = file['test']

    print(test)


def jpickle():
    frozen = jsonpickle.encode(d)
    with open(PICKLE_FILE, 'w') as file:
        json.dump(frozen, file, indent=2)


def junpickle():
    global d
    with open(PICKLE_FILE, 'r') as file:
        frozen = json.load(file)
        d = jsonpickle.decode(frozen)


def get_ids():
    # For testing
    ids = []
    for item in d.values():
        for subitem in item.values():
            if subitem.id:
                ids.append(subitem.id)
    print(ids)


def main():
    junpickle()
    print('********INBOX*********')
    d['inbox'].print()
    print('*******CALENDAR*******')
    d['calendar'].print_upcoming(30)
    print('*****NEXT ACTIONS*****')
    d['next_actions'].print()
    print()
    jpickle()


if __name__ == '__main__':
    main()
