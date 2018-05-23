# Discarded code fragments. CSV parsing, sqlite...could be useful at some point.


def create_table(c):
    """Create the table if it does not exist already."""
    # TODO: Check if the table exists in the the file.
    c.execute("""CREATE TABLE waist_size(
        date DATE NOT NULL, waist_size INTEGER, PRIMARY KEY(date)""")


def get_current_waist():
    # Returns most recent waist measurement in cm.
    current_waist = None
    try:
        with open(WAIST_FILE, 'r') as file:
            lines = file.readlines()
            lastline = lines[-1].split(',')
            current_waist = int(lastline[1])
    except FileNotFoundError:
        print('No waist records were found.')
    if current_waist:
        return current_waist
    else:
        return None


def get_current_shoulders():
    # Returns most recent waist measurement in cm.
    current_shoulders = None
    try:
        with open(SHOULDER_FILE, 'r') as file:
            lines = file.readlines()
            lastline = lines[-1].split(',')
            current_shoulders = int(lastline[1])
    except FileNotFoundError:
        print('No shoulder records were found.')
    if current_shoulders:
        return current_shoulders
    else:
        return None


# def print_goals():


def add_record(date, measurement):
    # Uses csv for storage. If date already exists, update value.

    # Make sure data is valid
    try:
        newdate = parser.parse(date).strftime('%Y-%m-%d')
        newnum = int(measurement)
    except ValueError:
        print('Invalid input!')
        raise
    newrecord = [newdate, newnum]
    print(newrecord)
    update = False  # flag if record for date exists

    # Parse csv into multidimensional array
    records = []
    with open(WAIST_FILE, 'r') as file:
        line = file.readline()
        while line:
            thisline = line.split(',')
            try:
                date = parser.parse(thisline[0]).strftime('%Y-%m-%d')
                num = int(thisline[1])
            except ValueError:
                line = file.readline()
                continue

            if date == newdate:
                records.append(newrecord)
                update = True
                print('Record updated.')
            else:
                records.append([date, num])
            line = file.readline()

    if not update:
        records.append(newrecord)
        print('Record added.')
    records = sorted(records, key=lambda x: x[0])

    with open(WAIST_FILE, 'w+') as file:
        for record in records:
            s = str(record[0]) + ',' + str(record[1]) + '\n'
            file.write(s)

    return True


def main():

    height = 177  # cm
    ideal_waist = int(height * WAIST_HEIGHT_RATIO)
    ideal_shoulders = int(height * WAIST_HEIGHT_RATIO * GOLDEN_RATIO)
    today = time.strftime("%Y-%m-%d")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c',
        '--new-cm',
        action='store',
        dest='cm',
        help="input today's measurement in cm"
    )
    parser.add_argument(
        '-i',
        '--new-inches',
        action='store',
        dest='inches',
        help="input today's measurement in inches"
    )
    parser.add_argument(
        '-l',
        '--list-records',
        action='store_true',
        default=False,
        dest="list-records",
        help='print saved measurements'
    )

    args = parser.parse_args()

    if args.cm:
        add_record(today, args.cm)
        print("Target waist size: {} cm\nTarget shoulder size: {} cm".format(
            ideal_waist, ideal_shoulders))
    elif args.inches:
        measurement = in_to_cm(args.inches)
        add_record(today, measurement)
        print("Target waist size: {} in\nTarget shoulder size: {} in".format(
            cm_to_in(ideal_waist), cm_to_in(ideal_shoulders)))

    # # Check if we want to enter new data for today.
    # newinput = input("Enter new data? (y/n)\n>")
    # # If input begins with the letter 'y', the answer is 'yes'. Convert newinput to boolean.
    # newinput = newinput.lower().strip()[0] == 'y'

    # if newinput:
    #     # Get new waist size
    #     while True:
    #         try:
    #             waist = int(input(
    #                 "What is your waist size (in cm) today? (Enter any non-numeric string to skip.)\n>"))
    #         except ValueError:
    #             print("Value Error. Enter waist size as a whole number in cm.")
    #             continue
    #         else:
    #             break

    #     new_waist_data = (today, waist)

    #     while True:
    #         try:
    #             shoulders = int(input(
    #                 "What is your shoulder size (in cm) today? (Enter any non-numeric string to skip.)\n>"))
    #         except ValueError:
    #             print("Value Error. Enter waist size as a whole number in cm.")
    #             continue
    #         else:
    #             break

    #     new_shoulder_data = (today, shoulders)

    #     try:
    #         c.execute('''INSERT INTO waist_size
    #                  VALUES (?, ?)''', new_waist_data)
    #     except sqlite3.Error as e:
    #         print(e)

    #     try:
    #         c.execute('''INSERT INTO shoulder_size
    #                  VALUES (?, ?)''', new_shoulder_data)
    #     except sqlite3.Error as e:
    #         print(e)
    # else:
    #     c.execute('''SELECT waist_size
    #                          FROM waist_size
    #                          WHERE date =(
    #                                SELECT MAX(date) FROM waist_size);''')
    #     waist = c.fetchone()[0]
    #     print("Most recent waist size: {} cm".format(waist))
    #     c.execute('''SELECT shoulder_size
    #                          FROM shoulder_size
    #                          WHERE date =(
    #                                SELECT MAX(date) FROM shoulder_size);''')
    #     shoulders = c.fetchone()[0]
    #     print("Most recent shoulder width: {} cm".format(shoulders))

    # adonis_index = shoulders / waist
    # waist_height_ratio = waist / height
    # berate_user(waist_height_ratio)

    # print waist_size database
    # c.execute("SELECT * FROM waist_size")
    # rows = c.fetchall()
    # 94

    # conn.commit()
    # conn.close()
