#!/usr/local/env python3


class Event():
    def __init__(self, event, date):
        self.id = ''
        self.event = event
        self.date = date


class Action():
    def __init__(self, action):
        self.id = ''
        self.action = action


class Objective():
    def __init__(self, objective):
        self.id = ''
        self.objective = objective


def new_event(eventname, date):
    e = Event(eventname, date)


def main():
    conn = sqlite3.connect('./my_tracker.db')
    pass


if __name__ == '__main__':
    main()
