#!/usr/bin/env python3

import time
import json
import argparse
import datetime
from os import path, getcwd
from dateutil import parser
from shutil import copy2
from inspect import currentframe, getframeinfo
from pathlib import Path

GOLDEN_RATIO = (1 + 5 ** 0.5) / 2  # ≈1.618
WAIST_HEIGHT_RATIO = 0.447  # ideal waist-height ratio
# Get path script is executed from so the same data file is used regardless of
# where the script is called from.
THISFILE = getframeinfo(currentframe()).filename
PARENT = Path(THISFILE).resolve().parent
DATA_FILENAME = 'waist_tracker.json'
DATA_FILE = PARENT / DATA_FILENAME

data = {}
backup = True  # If true, daily backup will be made of data.
today = time.strftime("%Y-%m-%d")


def backup_json():
    """Create a backup copy of user data unless one was already created today."""
    filepath = PARENT / (DATA_FILENAME + '-' + today + '.bak')
    if not path.isfile(filepath):
        copy2(DATA_FILE, filepath)
        return True
    else:
        return False


def load_data():
    """Retrieve data from JSON file."""
    global data
    try:
        if backup:  # Create daily backup if flag set to true.
            backup_json()
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print('No user data.')


# For testing
load_data()
print(data)


def save_data():
    """Save data to json file."""
    print('saving data...')
    with open(DATA_FILE, 'w+') as file:
        json.dump(data, file)


def in_to_cm(inches):
    try:
        inches = int(inches)
    except ValueError:
        print("Invalid input")
        raise
    return round(inches * 2.54)


def cm_to_in(cm):
    try:
        cm = int(cm)
    except ValueError:
        print("Invalid input")
        raise
    return round(cm / 2.54)


def get_current_waist():
    # Returns most recent waist measurement in cm.
    if data:
        recent_date = max(list(data['waist']))
        print("Recent date: ", recent_date)
        return data['waist'][recent_date]
    else:
        print('Data not loaded.')
        return False


def get_current_shoulders():
    # Returns most recent waist measurement in cm.
    if data:
        recent_date = max(list(data['shoulders']))
        print("Recent date: ", recent_date)
        return data['shoulders'][recent_date]
    else:
        print('Data not loaded.')
        return False


# def print_goals():
    # TODO


def add_record(date, measurement, where):
    """Add or update measurement for date."""
    global data
    try:
        newdate = parser.parse(date).strftime('%Y-%m-%d')
        newnum = int(measurement)
    except ValueError:
        print('Invalid input!')
        raise
    # Update data if it exists, else add it.
    data[where][newdate] = newnum
    print('adding record...')
    print(data)
    save_data()
    return True


def berate_user(waist_height_ratio):
    """Encourages user to pursue goals."""
    print("Your current Adonis Index is {:.2f}".format(adonis_index))
    print(
        "Your current waist-to-height ratio is {:.2f}"
        .format(waist_height_ratio))
    if waist_height_ratio >= .53:
        print("""
    You're fat as fuck! Your health is at risk and you look disgusting!
    You have the risk equivalent to BMI of 25!
    Do something about it, fatty!
        """)
    elif waist_height_ratio >= .51:
        print("""
    You're still fat! You still have risk equivalent to BMI of 25!
    Lose more weight, fatso!
        """)
    elif waist_height_ratio >= .50:
        print("""
    You're still fat! Look at that gut! Gross!
        """)
    elif waist_height_ratio >= .49:
        print("""
    Better, but you're still too fat!
        """)
    elif waist_height_ratio >= .48:
        print("""
    You're getting there! Keep losing weight!
        """)
    elif waist_height_ratio >= .47:
        print("""
    Looking good! But don't start pigging out yet!
        """)
    else:
        print("""
    You are a god among men. Get more muscle, and don't get fat again!
        """)


def main():

    height = data['height']  # cm
    ideal_waist = int(height * WAIST_HEIGHT_RATIO)
    ideal_shoulders = int(height * WAIST_HEIGHT_RATIO * GOLDEN_RATIO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c',
        '--new-cm',
        action='store',
        type=int,
        dest='cm',
        help="input today's measurement in cm"
    )
    parser.add_argument(
        '-i',
        '--new-inches',
        action='store',
        type=int,
        dest='inches',
        help="input today's measurement in inches"
    )
    parser.add_argument(
        '-l',
        '--list-records',
        action='store_true',
        dest="list-records",
        help='print saved measurements'
    )
    parser.add_argument(
        '-s',
        '--shoulders',
        action='store_true',
        dest='shoulders',
        help='record shoulder measurement. default is waist measurement.'
    )

    args = parser.parse_args()

    if args.cm and not args.shoulders:
        add_record(today, args.cm, 'waist')
        print("Target waist size: {} cm\nTarget shoulder size: {} cm".format(
            ideal_waist, ideal_shoulders))
    elif args.inches and not args.shoulders:
        measurement = in_to_cm(args.inches)
        add_record(today, measurement, 'waist')
        print("Target waist size: {} in\nTarget shoulder size: {} in".format(
            cm_to_in(ideal_waist), cm_to_in(ideal_shoulders)))
    elif args.shoulders and not args.inches:
        add_record(today, args.cm, 'shoulders')
        print("Target waist size: {} cm\nTarget shoulder size: {} cm".format(
            ideal_waist, ideal_shoulders))
    elif args.inches and args.shoulders:
        measurement = in_to_cm(args.inches)
        add_record(today, measurement, 'shoulders')
        print("Target waist size: {} in\nTarget shoulder size: {} in".format(
            cm_to_in(ideal_waist), cm_to_in(ideal_shoulders)))


if __name__ == '__main__':
    main()
