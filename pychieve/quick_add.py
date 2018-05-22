#!/usr/bin/env python3
import argparse
from pygtd import load_data, save_data, add_to_inbox, inbox_popup
from os import path
from time import time

data = {}


def main():
    load_data()
    inbox_popup()
    save_data()


if __name__ == '__main__':
    main()
