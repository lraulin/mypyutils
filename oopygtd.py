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

# Ensure filepath for data files is in module directory regardless of cwd.
FILENAME = getframeinfo(currentframe()).filename
PARENT = Path(FILENAME).resolve().parent
DATA_FILE = PARENT / 'pygtd.json'
PICKLE_FILE = PARENT / 'pickle.json'


def timedif(then):
    """Return time difference between now and Unix timestamp in seconds."""

    difsec = time() - then
    return round(difsec)


def confirm_date_parse():
    """Prompt user for date and confirm accuracy. Return datetime object.

    Allow user to enter date in any format. Confirm date has been parsed
    correctly before continuing.

    """
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
    """Print word in center of line surrounded by specified character. 

    For printing titles. Ie:
    ******************************TITLE******************************

    """
    length = floor((size - len(title))/2)
    text = (pad * length) + title + (pad * length)
    if len(title) % 2 != 0:
        text += pad
    print(text)


def timer(seconds):
    """Display countdown for specified time."""
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
    """Create item base class."""
    id_count = 0  # Was meant to provide each item a unique id number.
    # It's not currently used for anything, and the timestamp can serve the
    # purpose if necessary. May be discarded in the future.

    def __init__(self, created=None):
        """Initialize item.

        Assign timestamp if provided. Otherwise create timestamp now.

        """

        self.__class__.id_count += 1
        self.id = self.__class__.id_count
        self.created = created if created else time()
        self.completed = None

    def age(self):
        """Return difference between now and item's timestamp in seconds."""

        return timedif(self.created)


class InboxItem(Item):
    """Create Inbox item.

    Basically just a line of text to store ideas about things might need or
    want to do something about.

    """

    def __init__(self, text, created=None):
        """Initialize Inbox item."""
        Item.__init__(self, created)
        self.text = text


class Inbox():
    """Create Inbox container object.

    Stores collection of Inbox items and associated actions. Dequeue is used
    as most common operation will be FIFO processing of items."""

    def __init__(self, items=deque()):
        """Initialize queue for Inbox items."""
        self.items = items

    def add(self, text):
        """Add new Inbox item."""
        item = InboxItem(text)
        self.items.append(item)

    def print(self):
        """Print Inbox item."""
        for item in self.items:
            print(str(item.id) + ' ' + item.text)

    def quickadd(self):
        """Display a prompt to add new Inbox item.

        For use with global keyboard shortcut to create popup terminal for rapid
        task entry.
        """
        text = input('INBOX> ')
        self.add(text)

    def paste(self):
        """Save clipboard contents as new Inbox item."""
        self.add(pyperclip.paste())


class NextAction(Item):
    """Create Next Action.

    Basically todos. Should contain a description of a specific physical
    action you must perform.

    """

    def __init__(self, text, context=None, created=None):
        Item.__init__(self, created)
        self.text = text
        # contexts not yet implimented as I personally have only one context
        # at the moment.
        self.context = context


class NextActionList():
    """Create Next Action container."""

    def __init__(self, items=[]):
        """Initialize list for Next Actions."""
        self.items = items

    def print(self):
        """Print Next Action."""
        for item in self.items:
            print(str(item.id), item.text)

    def i_new_item(self, created=None):
        """Create new item with interactive prompt."""
        print("Next Action: What's the next thing you need to do to move toward "
              + "the desired outcome?\nVisualize yourself doing it and describe it "
              + "in a sentence. Be specific. Ie not 'set up meeting', but 'pick up "
              + "the phone and call X'.")
        text = input("> ")
        newitem = NextAction(text, created)
        self.items.append(newitem)
        print('New item added to Next Actions list.')


class WaitingFor(Item):
    """Create WaitingFor item.

    Todos that you are waiting for someone else to do, or something that you
    are waiting to happen before you can move forward on something else.

    """

    def __init__(self, text, who='', due=None, created=None):
        """Initialize Waiting For item."""
        Item.__init__(self, created)
        self.created = time()
        self.who = who
        self.text = text
        self.due = due


class WaitingForList():
    """Create Waiting For item container."""

    def __init__(self, items=[]):
        """Initialize list for Waiting For items."""
        self.items = items

    def print(self):
        """Print Waiting For items."""

        today = datetime.datetime.today()
        for item in self.items:
            days = (item.due - today).days if item.due else None
            text = '...' + item.text
            if item.who:
                text += ' from ' + item.who
            if days:
                text += ' in ' + str(days) + ' days'
            print(text)

    def i_new_item(self, created=None):
        """Create new item with interactive prompts."""

        print('Who are you waiting on to do this? (Press Enter to skip.)')
        who = input('> ')
        print('What are you waiting for?')
        text = input('> ')
        print('When do you expect it to happen?')
        due = confirm_date_parse()
        newitem = WaitingFor(text, who, due, created)
        self.items.append(newitem)
        print('New item added to Waiting For list.')


class Project(Item):
    """Create Project.

    For desired outcomes/multistep todos/goals. Should contain a specific
    description of outcome/what counts as 'done'. Each should be associated with
    at least one Next Action--the very next specific physical action necessary
    to move forward to the desired outcome.

    """

    def __init__(self, text, short_name, next_actions=[], created=None):
        Item.__init__(self, created)
        self.text = text
        self.short_name = short_name
        self.next_actions = next_actions


class ProjectList():
    """Create container for Project items."""

    def __init__(self, items=[]):
        """Initialize ProjectList."""
        self.items = items

    def print(self):
        for item in self.items:
            print('[{}] {}'.format(item.short_name, item.text))
            # TODO: print next action

    def i_new_item(self, created=None):
        """Interactively create new item."""

        text = input("Project: What's the desired outcome? What are you committed "
                     + "to accomplishing or finishing about this? What would 'done'"
                     + " look like?\n> ")
        short_name = input("Short name: ")
        newitem = Project(text, short_name, created=created)
        self.items.append(newitem)
        print('New Project added to Projects list.')


class MaybeSomeday(Item):
    """Create Maybe Someday item.

    Ideas about things to maybe do someday/todos you are not fully committed
    to doing but might want to reconsider in the future. Can be created from
    inbox text without modification.

    """

    def __init__(self, text, category='', created=None):
        Item.__init__(self, created)
        self.text = text
        self.category = category


class MaybeSomedayList():
    """Container for MaybeSomeday items."""

    def __init__(self, items=[]):
        self.items = items

    def add(self, text, created=None):
        newitem = MaybeSomeday(text, created=created)
        self.items.append(newitem)


class CalendarItem(Item):
    """Create Calendar item.

    Used for events, appointments, deadlines, or other items associated with a 
    specific future date/time.

    """

    def __init__(self, date, text, created=None):
        Item.__init__(self, created)
        self.date = date
        self.text = text

    # TODO: maybe someday sync with Google Calendar


class Calendar():
    """Create container for Calendar items."""

    def __init__(self, items=[]):
        self.items = items

    def add(self, item):
        self.items.append(item)

    def i_new_item(self, created=None):
        """Interactively create new Calendar item."""

        text = input("Describe scheduled item:\n> ")
        ok = False
        # Use dateutil to parse any date input, such june 2, tues, next week,
        # etc. Confirm parse was accurate before continuing.
        while not ok:
            when = input(
                "Date (and time, optional)\nAny format should work:\n> ")
            when = str(parser.parse(when))
            print("Date/Time: {}".format(when))
            isok = input("Ok? (y/n)").lower()
            if 'y' in isok:
                ok = True
        newitem = CalendarItem(when, text, created)
        self.items.append(newitem)
        print('New item added to Calendar.')

    def print_upcoming(self, period=30):
        """Print Calendar items.

        Print all future calendar items within given number of days, the
        date/time at which they occur, and the time between now and then.

        """
        today = datetime.datetime.today()
        self.items.sort(key=attrgetter('date'))
        for item in self.items:
            delta = item.date - today
            days = delta.days
            # only print dates that are not in the past and in specified range
            if days <= period and item.date >= today:
                date = item.date.strftime('%a, %b %d')
                time = item.date.strftime('%I:%M%p')
                # If time in datetime object is 00:00, assume specific time was
                # not entered or desired.
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
    """Create container for completed items.

    Completed items can be of any (GTD list item) type.

    """

    def __init__(self, items=[]):
        self.items = items


class GTD():
    """Create main program object.

    This object stores program data, and is responsible for saving and loading,
    importing and exporting, for handling interactions between container
    objects, etc.

    """

    def __init__(self):
        """Initialize dictionary to store program data."""
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
        """Import data from human-readable JSON file used in app prototype."""

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
        """Encode objects and store in JSON file."""
        # No JSON formatter can make sense of the file, so I'm not sure what
        # the advantage is vs. binary storage, but it does the trick.
        frozen = jsonpickle.encode(self.d)
        with open(PICKLE_FILE, 'w') as file:
            json.dump(frozen, file, indent=2)

    def junpickle(self):
        """Restore encoded objects from JSON file.

        From jsonpickle docs:

        WARNING: Jsonpickle can execute arbitrary Python code. Do not load 
        jsonpickles from untrusted / unauthenticated sources.

        """
        with open(PICKLE_FILE, 'r') as file:
            frozen = json.load(file)
            self.d = jsonpickle.decode(frozen)

    def print_overview(self):
        """Call the print methods for container objects."""

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
        """Display interactive prompts for user to process inbox items.

        FIFO. For each item, the user will be guided
        by interactive prompts to create a new item based on inbox item. New
        item will be given same timestamp as the inbox item. (Conceptually, the
        item is being 'moved' or 'changed'.) When item is successfully
        processed, it will be dequeued (removed), and loop will continue with
        next (now first) item in queue. Loop until no items are left.

        """
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
                self.d['next_actions'].i_new_item(item.created)
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
                self.d['calendar'].i_new_item(item.created)
                inbox.popleft()
                continue
            elif 'w' in actionable:
                # Create new Waiting For item
                self.d['waiting_for'].i_new_item(item.created)
                inbox.popleft()
                continue
            elif 'p' in actionable:
                # Create new Project
                self.d['projects'].i_new_item(item.created)
                continue
            elif 's' in actionable:
                # save item in SomedayMaybe for future consideration
                self.d['someday_maybe'].add(item.text, item.created)
                inbox.popleft()
                continue
            elif 'r' in actionable:
                # TODO: add reference list
                print('Not implemented')
                continue
            elif 't' in actionable:
                # delete item
                inbox.popleft()
                print('Item deleted.')
                continue
            else:
                print('Invalid input')


def main():
    # only one argument is meant to be used at a time, but you could, say,
    # add an inbox item and view the lists at the same time if you wanted to

    # TODO: handle inappropriate option combinations

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

    # instantiate object responsible for data
    gtd = GTD()

    # load data from file
    # gtd.import_json()
    gtd.junpickle()

    if args.inbox:  # -i, --inbox
        # add text entered at CLI to inbox
        text = ' '.join(args.inbox)
        gtd.d['inbox'].add(text)
    if args.paste:  # -P, --paste
        # add clipboard contents to inbox
        gtd.d['inbox'].paste()
    if args.overview:  # -o, --overview
        # print lists
        gtd.print_overview()

    # save data to file
    gtd.jpickle()


if __name__ == '__main__':
    main()
