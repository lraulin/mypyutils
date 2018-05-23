#!/usr/bin/env python3

import argparse
import json
import pyperclip
from os import path
from time import time, sleep
from sys import stdout
from dateutil import parser
from inspect import currentframe, getframeinfo
from pathlib import Path

# TODO: suppress help message when option is used without positional argument
# TODO: shortcut key popup for inbox entry. First use terminal. Maybe later do
# it with a gui window
'''First, set up GTD flow:
add to inbox
process inbox
'''

# Get path script is executed from so the same data file is used regardless of
# where the script is called from.
FILENAME = getframeinfo(currentframe()).filename
PARENT = Path(FILENAME).resolve().parent
DATA_FILE = PARENT / 'pygtd.json'

data = {
    'inbox': {},
    'actions': {},
    'projects': {},
    'someday_maybe': {},
    'waiting_for': {},
    'scheduled': {},
    'reference': {}
}

# add to inbox from cli
# add to inbox from clipboard
# process inbox
# list


def load_data():
    """Retrieve data from JSON file."""
    global data
    if not path.isfile(DATA_FILE):
        with open(DATA_FILE, 'w') as file:
            json.dump(data, file)
    else:
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)


def save_data():
    """Save data to json file."""
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)


def add_to_inbox(text):
    global data
    time_stamp = time()
    data['inbox'][time_stamp] = text
    print(data)
    save_data()
    print('Item added to inbox: {}'.format(text))


def empty(container):
    global data
    print("Erase all contents from {}.".format(container))
    confirmation = input("Are you sure? (y/n): ")
    if 'y' in confirmation:
        if data[container]:
            data[container] = {}
            save_data()
        else:
            print("{} is already empty.".format(container))
    else:
        print("Command aborted.")


def process_inbox():
    keylist = list(data['inbox'].keys())
    for index, key in enumerate(keylist, start=1):
        process_inbox_item(index, len(keylist), key)


def timer(duration):
    seconds = duration % 60
    minutes = round(duration / 60)

    while True:
        try:
            stdout.write("\r{minutes}:{seconds}".format(
                minutes=minutes, seconds=seconds))
            stdout.flush()
            sleep(1)
            if seconds >= 0:
                minutes -= 1
                seconds = 60
        except KeyboardInterrupt:
            break
    print("Time's up!")
    # TODO: add alarm sound


def delete_from_inbox(id):
    del data['inbox'][id]
    save_data()
    print('Item removed from Inbox.')
    return True


def new_action(id=time()):
    global data
    print("Next Action: What's the next thing you need to do to move toward "
          + "the desired outcome?\nVisualize yourself doing it and describe it "
          + "in a sentence. Be specific. Ie not 'set up meeting', but 'pick up "
          + "the phone and call X'.")
    text = input("> ")
    data['actions'][id] = text
    save_data()
    print('Item added to Next Actions list.')


def new_appointment(id=time()):
    text = input("Describe scheduled item:\n> ")
    ok = False
    while not ok:
        when = input("Date (and time, optional)\nAny format should work:\n> ")
        when = str(parser.parse(when))
        print("Date/Time: {}".format(when))
        isok = input("Ok? (y/n)").lower()
        if 'y' in isok:
            ok = True
    data['scheduled'][id] = {'date': when, 'text': text}
    save_data()
    print('Appointment added to Scheduled list.')


def new_project(id=time()):
    text = input("Project: What's the desired outcome? What are you committed "
                 + "to accomplishing or finishing about this? What would 'done'"
                 + " look like?\n> ")
    short_name = input("Short name: ")
    data['projects'][id] = {'short_name': short_name, 'text': text}
    save_data()


def process_inbox_item(num, total, id):
    global data
    print("\nProcess Item:")
    print('\t({}/{}) {}\n'.format(num, total, data['inbox'][id]))
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
        new_action(id)
        delete_from_inbox(id)
    elif 'd' in actionable:
        print("Do it now!")
        input("Press any key to start 2 min timer...")
        timer(120)
        done = input("Done? (y/n): ").lower()
        if 'y' in done:
            delete_from_inbox(id)
            save_data()
        else:
            process_inbox_item(num, total, id)
    elif 'c' in actionable:
        new_appointment(id)
        delete_from_inbox(id)
    elif 'w' in actionable:
        data['waiting'][id] = data['inbox'][id]
        delete_from_inbox(id)
        save_data()
    elif 'p' in actionable:
        new_project(id)
    elif 's' in actionable:
        data['someday_maybe'][id] = data['inbox'][id]
        delete_from_inbox(id)
        save_data()
        print('Item added to Someday/Maybe list.')
    elif 'r' in actionable:
        data['reference'][id] = data['inbox'][id]
        delete_from_inbox(id)
        save_data()
        print('Item added to Reference list.')
    elif 't' in actionable:
        delete_from_inbox(id)
    else:
        print('Invalid input')
        process_inbox_item(num, total, id)


def daily_revew():
    # TODO: print calendar items with dates/days remaining, and next actions
    pass


def inbox_prompt():
    while True:
        print("Enter everything you can think of that you might want to do "
              + "something about. Enter 'q' when done.")
        text = input("INBOX> ")
        if text == 'q':
            break
        add_to_inbox(text)


def weekly_review():
    # Empty your head
    inbox_prompt()
    # Review projects list; decide next action for each one
    # Review next actions; mark off if completed
    # Review waiting for
    # Review checklists
    # Review Someday/Maybe
    pass


def inbox_popup():
    text = input("INBOX> ")
    add_to_inbox(text)


def bigger_picture_review():
    # TODO
    pass


def main():
    global data
    load_data()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input',
        nargs='*',
        default=''
    )
    # Options for selecting container (inbox, actions, projects, etc) to
    # perform action (add, list, delete, etc) on. Only one container may be
    # selected.
    container_group = parser.add_mutually_exclusive_group()
    container_group.add_argument(
        '-i',
        '--inbox',
        action='store_true',
        dest='inbox',
        help='Inbox'
    )
    container_group.add_argument(
        '-n',
        '--next-actions',
        action='store_true',
        dest='next',
        help='Next Actions'
    )
    container_group.add_argument(
        '-p',
        '--projects',
        action='store_true',
        dest='projects',
        help='Projects.'
    )
    container_group.add_argument(
        '-s',
        '--someday-maybe',
        action='store_true',
        dest='someday_maybe',
        help='Someday/Maybe'
    )
    container_group.add_argument(
        '-w',
        '--waiting_for',
        action='store_true',
        dest='waiting_for',
        help='Waiting for.'
    )
    container_group.add_argument(
        '-c',
        '--scheduled',
        action='store_true',
        dest='scheduled',
        help='Scheduled (Calendar).'
    )
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        '-l',
        '--list',
        action='store_true',
        dest='list',
        help='list contents. Combine with container argument.'
    )
    action_group.add_argument(
        # TODO: For testing! Remove, or add confirmation dialogue
        '-e',
        '--empty',
        action='store_true',
        dest='empty',
        help='empty container'
    )
    parser.add_argument(
        '-d',
        '--process-inbox',
        action='store_true',
        help='Process inbox. ("d" is for "daily".)'
    )
    parser.add_argument(
        '-q',
        '--quick',
        dest='quick',
        action='store_true',
        help='Prompt for inbox for use with hotkey.'
    )

    args = parser.parse_args()
    text = ' '.join(args.input) if args.input else pyperclip.paste()
    print(args)

    # set container
    container = None
    if args.inbox:
        container = 'inbox'
    elif args.next:
        container = 'next_actions'
    elif args.projects:
        container = 'projects'
    elif args.someday_maybe:
        container = 'someday_maybe'
    elif args.waiting_for:
        container = 'waiting_for'
    elif args.scheduled:
        container = 'scheduled'

    # set action
    action = None
    if args.quick:
        inbox_popup()
        return True

    if args.empty:
        action = 'empty'

    if not container and not action:
        add_to_inbox(text)

    if args.process_inbox:
        process_inbox()

    if args.empty:
        if container:
            empty(container)
        else:
            print('Container to empty must be specified.')


if __name__ == '__main__':
    main()