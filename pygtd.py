#!/usr/bin/env python3

import argparse
import json
import pyperclip
import datetime
import re
from os import path
from time import time, sleep
from sys import stdout, argv, exit
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


def days_remaining(date_string):
    future_date = parser.parse(date_string)
    delta = future_date - datetime.datetime.now()
    return delta.days


def add_to_inbox(text):
    global data
    time_stamp = time()
    data['inbox'][time_stamp] = text
    save_data()
    print('Item added to inbox: {}'.format(text))


def file_to_inbox():
    """Add each line of a plain text file as a new Inbox item."""
    with open(argv[1], 'r') as f:
        for line in f:
            add_to_inbox(line)


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
    if len(keylist) == 0:
        print('Your Inbox is empty!')
        return False
    for index, key in enumerate(keylist, start=1):
        process_inbox_item(index, len(keylist), key)
    return True


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


def delete_from_inbox(id, container='inbox'):
    del data[container][id]
    save_data()
    print('Item removed from ' + container + '.')
    return True


def complete(id, container='actions'):
    dt = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
    text = data[container][id]
    try:
        data['completed'][id] = {'completion_date': dt, 'text': text}
    except KeyError:
        data['completed'] = {}
        data['completed'][id] = {'completion_date': dt, 'text': text}

    delete_from_inbox(id, container)
    return True


def new_action(id):
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
        try:
            data['waiting'][id] = data['inbox'][id]
            delete_from_inbox(id)
        except KeyError:
            data['waiting'] = {}
            data['waiting'][id] = data['inbox'][id]
            delete_from_inbox(id)
    elif 'p' in actionable:
        new_project(id)
    elif 's' in actionable:
        data['someday_maybe'][id] = data['inbox'][id]
        delete_from_inbox(id)
        save_data()
        print('Item added to Someday/Maybe list.')
    elif 'r' in actionable:
        try:
            data['reference'][id] = data['inbox'][id]
            delete_from_inbox(id)
        except KeyError:
            data['reference'] = {}
            data['reference'][id] = data['inbox'][id]
            delete_from_inbox(id)
        print('Item added to Reference list.')
    elif 't' in actionable:
        delete_from_inbox(id)
    else:
        print('Invalid input')
        process_inbox_item(num, total, id)


def print_actions():
    while True:
        keylist = list(data['actions'])
        print('\nNext Actions:')
        for i, key in enumerate(keylist):
            print('  ' + str(i) + ' ' + data['actions'][key])
        print(
            'Enter number (if appropriate) followed by command [ie 1 d, 5t]:')
        print('(#d)one, (#t)rash, (#e)dit, (q)uit')
        choice = input('> ').lower()
        re_num = re.compile(r'\d*')
        re_char = re.compile('[a-z]')
        num = re_num.search(choice)
        num = num.group()
        action = re_char.search(choice)
        if num:
            num = int(num)
        if action:
            action = action.group()
        if 'q' == action:
            print('Goodbye!')
            break
        if num and num >= len(keylist):
            print('Value out of range.')
            continue
        if action == 't':
            print('Delete task: ' + data['actions'][keylist[num]])
            confdelete = input('(y/n)').lower()
            if 'y' in confdelete:
                delete_from_inbox(keylist[num])
            else:
                continue
        elif action == 'd':
            complete(keylist[num])
            continue
        elif action == 'e':
            print('Not implimented')
            continue
        else:
            print('Invalid input')
            continue


# def print_calendar():
    # for item in data['schedule']:


def process_projects():
    global data
    for project in data['projects']:
        if not data['projects'][project]['next_actions']:
            data['projects'][project]['next_actions'] = []
        if len(data['projects'][project]['next_actions']) == 0:
            print('=' * 80)
            print('Project:', data['projects'][project]['text'])
            print('=' * 80)
            id = time()
            new_action(id)
            data['projects'][project]['next_actions'].append(str(id))
            save_data()
    print('\nDone processing projects!\n')


def list_projects():
    print('')
    print('============')
    print('| Projects |')
    print('============')
    for id in data['projects']:
        print(data['projects'][id]['text'])
        if not data['projects'][id]['next_actions']:
            print('    No Next Action! Time to review projects!')
        for action in data['projects'][id]['next_actions']:
            print('  >', data['actions'][action])


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
    parser.add_argument(
        '-i',
        '--inbox',
        action='store_true',
        help='Inbox'
    )
    parser.add_argument(
        '-n',
        '--next-actions',
        dest='next_actions',
        action='store_true',
        help='Next Actions'
    )
    parser.add_argument(
        '-d',
        '--process-inbox',
        dest='process_inbox',
        action='store_true',
        help='Process inbox. ("d" is for "daily".)'
    )
    parser.add_argument(
        '-q',
        '--quick-add',
        dest='quick',
        action='store_true',
        help='Prompt for inbox for use with hotkey.'
    )
    parser.add_argument(
        '-p',
        '--process-projects',
        dest='process_projects',
        action='store_true',
        help='Review project list and decide next actions.'
    )
    parser.add_argument(
        '-l',
        '--list',
        action='store_true',
        help='Modifies option to show list. Combine with -p.'
    )
    parser.add_argument(
        '-f',
        '--import-file',
        dest='import_file',
        action='store_true',
        help='Add each line in plain text file as new Inbox item.'
    )

    args = parser.parse_args()
    text = ' '.join(args.input) if args.input else pyperclip.paste()
    print(args)

    if args.quick:
        inbox_popup()
        return True

    if args.inbox:
        add_to_inbox(text)

    if args.process_inbox:
        process_inbox()

    if args.next_actions:
        print_actions()

    if args.process_projects and args.list:
        list_projects()
    elif args.process_projects:
        process_projects()

    if args.import_file:
        file_to_inbox()


if __name__ == '__main__':
    main()
