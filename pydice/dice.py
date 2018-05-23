#!/usr/bin/env python3

from random import randrange, randint, gauss
from sys import argv
import re

FUDGE_SCALE = {
    7: 'Legendary+++',
    6: 'Legendary++',
    5: 'Legendary+',
    4: 'Legendary',
    3: 'Superb',
    2: 'Great',
    1: 'Good',
    0: 'Fair',
    -1: 'Mediocre',
    -2: 'Poor',
    -3: 'Terrible',
    -4: 'Abysmal'
}


def roll(number, sides, modifier=0):
    result = 0
    for _ in range(number):
        result += randrange(sides) + 1
    return result + modifier


def roll3d6():
    return roll(3, 6)


def gaussian_3d6():
    mean = 10.5
    sd = 2.958
    rank = 5
    mean += rank * 1
    sd -= rank * .1
    return int(gauss(mean, sd))

# for i in range(10):
#     print(gaussian_3d6())


def roll_sd():
    # Returns a standard deviation with odds of result proportional to normal distribution
    return round(gauss(0, 1), 2)


def random_iq():
    return int(gauss(100, 15))


# for i in range(10):
#     print('%.1f' % roll_sd())


def random_height(sex='m', units='in', mean=None, sd=None):
    """
    :param sex:     m or f for male or female; default male
    :param units:   in, ft, imperial, cm, or m; default in
    :param mean:    Average height; if none, use US stats
    :param sd:      Average standard deviation; if none, use US stats
    :return:        Random height with chance proportional to normal distribution
    """
    conversions = {'cm': 2.54, 'm': .024, 'ft': 0.0833333}
    male_mean = 69.1
    male_sd = 2.9
    female_mean = 67.7
    female_sd = 2.7
    if mean != None:
        pass
    elif sex == 'm':
        mean = male_mean
    elif sex == 'f':
        mean = female_mean
    else:
        raise ValueError('Incorrect parameters')
    if sd != None:
        pass
    elif sex == 'm':
        sd = male_sd
    elif sex == 'f':
        sd = female_sd
    else:
        raise ValueError('Incorrect parameters')
    height = gauss(mean, sd)
    if units == 'in':
        height = str(int(height)) + " in"
    elif units == 'imperial':
        feet = int(height * conversions['ft'])
        inches = height - (feet * 12)
        height = str(feet) + "'" + str(int(inches)) + '"'
    elif units == 'ft':
        height = height * conversions[units]
        height = str.format("{0:.1f}", height)
    elif units == 'cm':
        height = str(int(height * conversions[units])) + " " + units
    elif units == 'm':
        height = height * conversions[units]
        height = str.format("{0:.2f}", height) + ' m'
    else:
        raise ValueError
    return height

# for i in range(10):
#     print(random_height(units = 'm'))


def rolld20():
    return roll(1, 20)


def rolldF(num, mod):
    result = 0
    for _ in range(num):
        result += randrange(3) - 1
    result += mod
    return result


def roll_fudge(num, mod):
    roll = int(rolldF(num, mod))
    print('{} ({:+})'.format(FUDGE_SCALE[roll], roll))
    return roll


def roll_percentile():
    roll(1, 100)


# 4d6, drop lowest
# can also take other types of dice, number of dice, and number of high rolls to keep
def roll_best(sides=6, dice=4, keep=3):
    rolls = []
    for _ in range(dice):
        rolls.append(randint(1, sides))
    # print(rolls)
    while len(rolls) > keep:
        rolls.remove(min(rolls))
    return sum(rolls)


# Set of D&D scores using 4d6b3 method
def gen_attributes():
    attributes = []
    for _ in range(6):
        attributes.append(roll_best())
    return attributes


def roll_owod(pool, difficulty, successes=0, reroll=False):
    # Roll using rules from Old World of Darkness
    no_successes = True
    any_ones = False

    for _ in range(pool):
        roll = randint(1, 10)
        if roll == 1 and reroll == False:
            successes -= 1
            any_ones = True
        elif roll == 10:
            roll_owod(pool, difficulty, successes, True)
        elif randint(1, 10) > difficulty:
            successes += 1
            no_successes = False

    if no_successes and any_ones:
        return "Botch!"

    return successes


def roll_nwod(pool, successes=0):
    # Roll using rules from New World of Darkness
    for _ in range(pool):
        roll = randint(1, 10)
        if roll == 1:
            successes -= 1
        elif roll == 10:
            roll_owod(pool, successes)
        elif randint(1, 10) >= 8:
            successes += 1

    return successes


def roll_gurps(skill, *args):
    # Skill the player's effective skill.
    # Returns result of die roll and degree and margin of success or failure.
    mod = sum(args)    # Take arbitrary number of modifiers to the roll
    success = ""
    roll = randint(1, 6) + randint(1, 6) + randint(1, 6) + mod
    margin = skill - roll    # Margin of success or failure
    if roll <= 4:
        success = "Critical Success"
    elif roll == 5 and skill >= 15:
        success = "Critical Success"
    elif roll == 6 and skill >= 16:
        success = "Critical Success"
    elif roll >= 18:
        success = "Critical Failure"
    elif roll >= 17 and skill <= 15:
        success = "Critical Failure"
    elif margin <= -10:
        success = "Critical Failure"
    elif roll <= skill:
        success = "Success"
    else:
        success = "Failure"
    if "Success" in success:
        passfail = True
    else:
        passfail = False

    return roll, success, margin, passfail


def gurps_quick_contest(skill1, skill2, mod1=0, mod2=0):
    # Returns margin of success for first actor
    # If negative, the absolute value is the margin of success for second actor.
    roll1 = roll_gurps(skill1 + mod1)[0]
    roll2 = roll_gurps(skill2 + mod2)[0]
    return roll1 - roll2


def gurps_regular_contest(skill1, skill2):
    winner = ''
    # If both skills are low, make the lower one 10, and
    # increase the other one by the same amount.
    if skill1 <= 6 and skill2 <= 6:
        if skill1 > skill2:
            skill2 = 10
            skill1 += 10 - skill2
        else:
            skill1 = 10
            skill2 += 10 - skill1
    while winner == '':
        pass


def gurps_long_task(hours, *args):
    """
    :param hours:   Total man-hours required to complete task.
    :param args:    Each arg is the skill of a worker.
    :return:
    """
    skills = list(args)
    day = 0
    total_work = 0
    success = False
    while success == False:
        day += 1
        days_work = 0
        for worker in skills:
            work = 0
            result = roll_gurps(worker)[1]
            if result == 'Critical Success':
                work = 12
            if result == 'Failure':
                work = 4
            if result == 'Critical Failure':
                hours -= randint(1, 6) + randint(1, 6)
            if result == 'Success':
                work = 8
            days_work += work
        print('Day {}: {} man-hours of work completed'.format(day, days_work))
        total_work += days_work
        if total_work >= hours:
            success = True

    return print('Task completed in {} days.'.format(day))


def main():
    argstring = ' '.join(argv[1:])
    # matches 3d100, 4dF, d6, etc optionally followed by +/- modifier
    pattern = re.compile(r"(\d*)d([Ff]|\d+)(\s?[+-]\s?\d+)*")
    match = pattern.match(argstring)
    print(match)
    print(match.groups)
    if not match:
        print('Invalid input')
        return False
    print(match)
    num = int(match.group(1)) if match.group(1) else 1
    sides = int(match.group(2)) if match.group(2).isdigit() else 'F'
    mod = int(match.group(3)) if match.group(3) else 0
    while True:
        result = roll(num, sides) if not sides == 'F' else roll_fudge(num, mod)
        print(result)
        input('Press any key to roll again. Ctrl-C to exit')


if __name__ == '__main__':
    main()
