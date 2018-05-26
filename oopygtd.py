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
from collections import deque
from math import floor

FILENAME = getframeinfo(currentframe()).filename
PARENT = Path(FILENAME).resolve().parent
DATA_FILE = PARENT / 'pygtd.json'
PICKLE_FILE = PARENT / 'pickle.json'


def timedif(then):
    """Returns time difference between now and Unix timestamp."""
    difsec = time() - then
    return round(difsec)


def confirm_date_parse():
    """Allows user to enter date in any format. Confirms date has been parsed
    correctly before continuing. Return datetime object."""
    ok = False
    while not ok:
        date = input("Date (and time, optional)\nAny format should work:\n> ")
        date = parser.parse(date)
        print("Date/Time: {}".format(str(date)))
        isok = input("Ok? (y/n)").lower()
        if 'y' in isok:
            ok = True
        else:
            print("Let's try again...")
    return date


def center_print(title, pad='*', size=80):
    """Prints word in center of line surrounded by ascii character. Ie
    ******************************TITLE******************************"""
    length = floor((size - len(title))/2)
    text = (pad * length) + title + (pad * length)
    if len(title) % 2 != 0:
        text += pad
    print(text)


def timer(seconds):
    # TODO: add alarm sound
    while True:
        try:
            print('              ', end='\r', flush=True)
            print('   ' + str(seconds), end='\r', flush=True)
            sleep(1)
            seconds -= 1
            if seconds < 0:
                break
        except KeyboardInterrupt:
            break
    print("Time's up!")


class Item:
    id_count = 0

    def __init__(self, created=None):
        self.__class__.id_count += 1
        self.id = self.__class__.id_count
        # Use timestamp if given, else create a new one.
        self.created = created if created else time()
        self.completed = None

    def age(self):
        return timedif(self.created)


class InboxItem(Item):
    def __init__(self, text, created=None):
        Item.__init__(self, created)
        self.text = text


class Inbox():
    """Stores collection of Inbox items and associated actions. Dequeue is used
    as most common operation will be FIFO processing of items."""

    def __init__(self, items=deque()):
        self.items = items

    def add(self, text):
        item = InboxItem(text)
        self.items.append(item)

    def print(self):
        for item in self.items:
            print(str(item.id) + ' ' + item.text)

    def quickadd(self):
        """Creates a prompt to add new Inbox item. For use with global keyboard
        shortcut to create popup terminal for rapid task entry."""
        text = input('INBOX> ')
        self.add(text)

    def paste(self):
        """Save clipboard contents as new Inbox item."""
        self.add(pyperclip.paste())


class NextAction(Item):
    def __init__(self, text, context=None, created=None):
        Item.__init__(self, created)
        self.text = text
        self.context = context


class NextActionList():
    def __init__(self, items=[]):
        self.items = items

    def print(self):
        for item in self.items:
            print(str(item.id), item.text)

    def i_new_item(self, created=None):
        """Create new item with interactive prompt."""
        # Interactively create a new Next Action and add it to the list.
        print("Next Action: What's the next thing you need to do to move toward "
              + "the desired outcome?\nVisualize yourself doing it and describe it "
              + "in a sentence. Be specific. Ie not 'set up meeting', but 'pick up "
              + "the phone and call X'.")
        text = input("> ")
        newitem = NextAction(text, created)
        self.items.append(newitem)
        print('New item added to Next Actions list.')


class WaitingFor(Item):
    def __init__(self, text, who='', due=None, created=None):
        Item.__init__(self, created)
        self.created = time()
        self.who = who
        self.text = text
        self.due = due


class WaitingForList():
    def __init__(self, items=[]):
        self.items = items

    def print(self):
        today = datetime.datetime.today()
        for item in self.items:
            days = (item.due - today).days if item.due else None
            text = '...' + item.text
            if item.who:
                text += ' from ' + item.who
            if days:
                text += ' in ' + str(days) + ' days'
            print(text)

    def i_new_item(self):
        print('Who are you waiting on to do this? (Press Enter to skip.)')
        who = input('> ')
        print('What are you waiting for?')
        text = input('> ')
        print('When do you expect it to happen?')
        due = confirm_date_parse()
        newitem = WaitingFor(text, who, due)
        self.items.append(newitem)
        print('New item added to Waiting For list.')


class Project(Item):
    def __init__(self, text, short_name, next_actions=[], created=None):
        Item.__init__(self, created)
        self.text = text
        self.short_name = short_name
        self.next_actions = next_actions


class ProjectList():
    def __init__(self, items=[]):
        self.items = items

    def print(self):
        for item in self.items:
            print('[{}] {}'.format(item.short_name, item.text))

    def i_new_item(self, created=None):
        text = input("Project: What's the desired outcome? What are you committed "
                     + "to accomplishing or finishing about this? What would 'done'"
                     + " look like?\n> ")
        short_name = input("Short name: ")
        newitem = Project(text, short_name, created=created)
        self.items.append(newitem)
        print('New Project added to Projects list.')


class MaybeSomeday(Item):
    def __init__(self, text, category='', created=None):
        Item.__init__(self, created)
        self.text = text
        self.category = category


class MaybeSomedayList():
    def __init__(self, items=[]):
        self.items = items

    def add(self, text, created=None):
        newitem = MaybeSomeday(text, created=created)


class CalendarItem(Item):
    def __init__(self, date, text, created=None):
        Item.__init__(self, created)
        self.date = date
        self.text = text


class Calendar():
    def __init__(self, items=[]):
        self.items = items

    def add(self, item):
        self.items.append(item)

    def i_new_item(self, created=None):
        text = input("Describe scheduled item:\n> ")
        ok = False
        while not ok:
            when = input(
                "Date (and time, optional)\nAny format should work:\n> ")
            when = str(parser.parse(when))
            print("Date/Time: {}".format(when))
            isok = input("Ok? (y/n)").lower()
            if 'y' in isok:
                ok = True
        newitem = CalendarItem(when, text, created)
        print('New item added to Calendar.')

    def print_upcoming(self, period=30):
        """Prints all future calendar items within given number of days, the
        date/time at which they occur, and the time between now and then."""
        today = datetime.datetime.today()
        self.items.sort(key=attrgetter('date'))
        for item in self.items:
            delta = item.date - today
            days = delta.days
            if days <= period:
                date = item.date.strftime('%a, %b %d')
                time = item.date.strftime('%I:%M%p')
                if not time == '12:00AM':
                    date += ' ' + time
                hours = round(delta.seconds / 3600)
                print('{{{}}} {} ({} days, {} hours)'.format(
                    date,
                    item.text,
                    days,
                    hours
                ))
        # TODO: test if date is within days or less in the future


class CompletedItemList():
    def __init__(self, items=[]):
        self.items = items


class GTD():
    """Creates object responsible for holding all lists and handling interaction
    between them."""

    def __init__(self):
        self.d = {
            'inbox': Inbox(),
            'calendar': Calendar(),
            'next_actions': NextActionList(),
            'waiting_for': WaitingForList(),
            'projects': ProjectList(),
            'maybe_someday': MaybeSomedayList(),
            'completed_items': CompletedItemList()
        }

    def import_json(self):
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)

        # Import Inbox
        for key, value in data['inbox'].items():
            newitem = InboxItem(value)
            newitem.created = key
            self.d['inbox'].items.append(newitem)

        # Import Next Actions
        for key, value in data['actions'].items():
            newitem = NextAction(value)
            newitem.created = key
            self.d['next_actions'].items.append(newitem)

        # Import Calendar
        for key, value in data['scheduled'].items():
            date = parser.parse(value['date'])
            newitem = CalendarItem(date, value['text'])
            newitem.created = key
            self.d['calendar'].add(newitem)

        # Import Waiting For
        for key, value in data['waiting'].items():
            date = parser.parse(value['due'])
            newitem = WaitingFor(value['text'], value['who'], date)
            newitem.created = key
            self.d['waiting_for'].items.append(newitem)

        # Import Projects
        for key, value in data['projects'].items():
            newitem = Project(
                value['text'], value['short_name'], value['next_actions'])
            newitem.created = key
            self.d['projects'].items.append(newitem)

        # Import Completed Items
        for key, value in data['completed'].items():
            newitem = NextAction(value['text'])
            newitem.created = key
            newitem.completed = value['completion_date']
            self.d['completed_items'].items.append(newitem)

    def jpickle(self):
        frozen = jsonpickle.encode(self.d)
        with open(PICKLE_FILE, 'w') as file:
            json.dump(frozen, file, indent=2)

    def junpickle(self):
        with open(PICKLE_FILE, 'r') as file:
            frozen = json.load(file)
            self.d = jsonpickle.decode(frozen)

    def print_overview(self):
        center_print('INBOX')
        self.d['inbox'].print()
        center_print('CALENDAR')
        self.d['calendar'].print_upcoming()
        center_print('NEXT ACTIONS')
        self.d['next_actions'].print()
        center_print('WAITING FOR')
        self.d['waiting_for'].print()
        center_print('PROJECTS')
        self.d['projects'].print()
        print()

    def process_inbox(self):
        """Process inbox items, FIFO. For each item, the user will be guided
        by interactive prompts to create a new item based on inbox item. New
        item will be given same timestamp as the inbox item. (Conceptually, the
        item is being 'moved' or 'changed'.) When item is successfully
        processed, it will be dequeued (removed), and loop will continue with
        next (now first) item in queue. Loop until no items are left."""

        inbox = self.d['inbox'].items
        while len(inbox):
            item = inbox[0]
            # Use correct singular/plural form.
            item_items = 'items' if len(self.d['inbox'].items) > 2 else 'item'
            print("\nProcess Item ({} {} left)".format(
                len(self.d['inbox'].items), item_items))
            print(item.text)
            actionable = input("(a) Add to Next Actions\n"
                               + "(d) Do it now in 2 minutes\n"
                               + "(c) Schedule it -- add to Calendar\n"
                               + "(w) Add to Waiting For list\n"
                               + "(p) Add to Projects list\n"
                               + "(s) Add to Someday/Maybe\n"
                               + "(r) Add to Reference\n"
                               + "(t) Already done/Trash\n"
                               + "> ").lower()
            if 'a' in actionable:
                # Create new Next Action
                self.d['next_actions'].i_new_action(item.created)
                inbox.popleft()
            elif 'd' in actionable:
                # Complete task now in 2 minutes
                print("Do it now!")
                input("Press any key to start 2 min timer...")
                timer(120)
                done = input("Done? (y/n): ").lower()
                if 'y' in done:
                    item.completed = datetime.datetime.now()
                    self.d['completed'].items.append(item)
                    inbox.popleft()
                else:
                    continue  # repeat loop with same item
            elif 'c' in actionable:
                # Create new Calendar item
                self.d['calendar'].i_new_item(item.created)  # not implimented
                inbox.popleft()
                continue
            elif 'w' in actionable:
                # Create new Waiting For item
                try:
                    self.d['waiting_for'].i_new_waiting_for(
                        created=item.created)
                    inbox.popleft()
                    continue
            elif 'p' in actionable:
                # Create new Project
                self.d['projects'].i_new_item(item.created)
                continue
            elif 's' in actionable:
                # TODO
                print('Not implemented')
                continue
            elif 'r' in actionable:
                # TODO
                print('Not implemented')
                continue
            elif 't' in actionable:
                inbox.popleft()
                print('Item deleted.')
                continue
            else:
                print('Invalid input')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i',
        '--inbox',
        nargs='+',
        action='store',
        help='Add text to new Inbox item.'
    )
    parser.add_argument(
        '-o',
        '--overview',
        action='store_true',
        help='Print lists to terminal.'
    )
    parser.add_argument(
        '-P',
        '--paste',
        action='store_true',
        help='Adds contents of clipboard as new Inbox item.'
    )
    args = parser.parse_args()
    gtd = GTD()
    gtd.junpickle()

    if args.inbox:
        text = ' '.join(args.inbox)
        gtd.d['inbox'].add(text)
    if args.paste:
        gtd.d['inbox'].paste()
    if args.overview:
        gtd.print_overview()

    # gtd.import_json()
    gtd.jpickle()


if __name__ == '__main__':
    main()
