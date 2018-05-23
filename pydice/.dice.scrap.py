# --------------------------------
# Test

# if __name__ == "__main__":
#     for i in range(10):
#         #print(roll_gurps_contested(11, 15))
#         #print(roll_gurps(10))
#         #print(roll_best())
#         print(gen_attributes())
#
#     gurps_long_task(100, 10, 10, 10)

# --------------------------------

# OOP version

# class Die():
#     def __init__(self, sides):
#         self.sides = sides
#
#     def roll(self, number):
#         result = 0
#         for i in range(number):
#             result += randrange(self.sides) + 1
#         return result
#
# class D6(Die):
#     def __init__(self):
#         self.sides = 6
#
# class GURPSRoll():
#
#     def __init__(self, skill, *args):
#         self.skill = skill
#         self.mod = sum(args)  # Take arbitrary number of modifiers to the roll
#         self.success = None
#         self.roll = randint(1, 6) + randint(1, 6) + randint(1, 6) + mod
#         self.margin = skill - roll  # Margin of success or failure
#         if roll <= 4:
#             self.success = True
#         elif roll >= 17:
#             self.success = False
#
#     def get_margin(self):
#         return self.margin
#
#     def get_success(self):
#         return self.success
#
# class GurpsLongTask():
#
#     def __init__(self, hours, *args):
#         skills = args
