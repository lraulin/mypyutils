import argparse
import json
import pyperclip
from os import path
from time import time, sleep
from sys import stdout
from dateutil import parser

# TODO: suppress help message when option is used without positional argument
# TODO: shortcut key popup for inbox entry. First use terminal. Maybe later do 
# it with a gui window
'''First, set up GTD flow:
add to inbox
process inbox
'''

DATA_FILE = 'pygtd.json'

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


def add_to_inbox(time_stamp, text):
    global data
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
    for key in keylist:
        process_inbox_item(key)


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
    save_data
    print('Item removed from Inbox.')
    return True


def new_action(id=time()):
    global data
    print("Next Action: What's the next thing you need to do to move toward "
          + "the desired outcome?\nVisualize yourself doing it and describe it in"
          + " a sentence.")
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


def process_inbox_item(id):
    global data
    print('\n{}'.format(data['inbox'][id]))
    actionable = input("Is it actionable? (y/n):").lower()
    if 'y' in actionable:
        steps = input("Can it be done in one step? (y/n):").lower()
        if 'y' in steps:
            print("What's the next action?")
            two_minutes = input(
                "Will it take less than 2 minutes? (y/n): ").lower()
            if 'y' in two_minutes:
                print("Do it now!")
                input("Press any key to start 2 min timer...")
                timer(120)
                done = input("Done? (y/n): ").lower()
                if 'y' in done:
                    delete_from_inbox(id)
                    save_data()
                else:
                    process_inbox_item(id)
            else:
                print("Delegate [add to Waiting For list (w)] or defer [add to Next"
                      + "Actions (a) or Scheduled Actions/Calendar (c)]?")
                later = input("> ").lower()
                if later[0] == 'w':
                    data['waiting'][id] = data['inbox'][id]
                    delete_from_inbox(id)
                    save_data()
                elif later[0] == 'a':
                    new_action(id)
                    delete_from_inbox(id)
                elif later[0] == 'c':
                    new_appointment(id)
                    delete_from_inbox(id)
        else:
            new_project(id)

    else:
        not_actionable = input(
            "(T)rash, (S)omeday/maybe, (R)eference: ").lower()
        if 't' in not_actionable:
            delete_from_inbox(id)
        elif 's' in not_actionable:
            data['someday_maybe'][id] = data['inbox'][id]
            delete_from_inbox(id)
            save_data()
            print('Item added to Someday/Maybe list.')
            # TODO: allow editing of new someday item.
        elif 'r' in not_actionable:
            data['reference'][id] = data['inbox'][id]
            delete_from_inbox(id)
            save_data()
            print('Item added to Reference list.')


def weekly_review():
    # TODO
    pass


def main():
    global data
    load_data()
    time_stamp = time()
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
    if args.empty:
        action = 'empty'

    if not container and not action:
        add_to_inbox(time_stamp, text)

    if args.process_inbox:
        process_inbox()

    if args.empty:
        if container:
            empty(container)
        else:
            print('Container to empty must be specified.')


if __name__ == '__main__':
    main()
