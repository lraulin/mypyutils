# Command-line Getting Things Done App

## Usage

pygtd.py new stuff for inbox\
pygtd.py -p # Process inbox\
pygtd.py -d # Review Next Actions

## Background

There are probably a million todo apps, and about half of them market
themselves as being good for GTD. Who needs another one? I've tried dozens.
(Some of my favorites are MyLife Organized, Effexis Achieve Planner (hasn't
been updated since 2007, but it still works just fine), Doit.im, and
EveryTask.) But surprisingly few do what I would like them to do: guide me
through/automate the process of applying GTD methodology. (EveryTask and
Achieve Planner come the closest.)

Many try to please everyone by being flexible, accommodating whatever approach
or combination of approaches you prefer. That's fine if you have a clearly
defined approach of your own, and the discipline to apply it consistently.
However, I find that it usually leads to me getting lost in the complexity, or
I just end up becoming lazy and inconsistent in my implementation, and
eventually stop using it entirely.

GTD can be life-changing, but the hard part is applying it completely and
sticking with it consistently. So I'm trying to make it easier by automating
the process. Rather than simply a todo app that CAN be used to apply GTD, I'm
writing a program to guide you through the process of actually applying GTD.

I've made several ways to quickly and easily capture any idea into your Inbox.
Then, when you decide to process your Inbox, it will go through each item,
FIFO, and you will be asked to decide what it is/what if anything you will do
about it. If it's a Next Action, you will be prompted to write a sentence
describing the specific physical action you will take, which will be added to
your Next Actions list. If it takes multiple steps, it's a Project, in which
case you will be prompted to describe what you're desired outcome is--what
exactly 'done' will look like. It's ok to decide to not decide; send it to your
Someday/Maybe list to reconsider later. By doing so, you have made a clear
distinction between things you are committed to getting done, and those you
aren't.

I've found a great deal of procrastination is really procrastination of decision-making. Setting aside time regularly to make decisions, and separating thinking from doing, is a big part of what makes GTD so powerful.

## Capturing Ideas to Your Inbox

For ease of use, make a short alias for pygtd. I use 'gt'. Then type the
command followed by text to be entered. Quotes are not necessary as long as you
don't use any special characters; if no optional argument flags are used (-i,
-q, etc), all arguments will be gathered into a single string, which will be
saved as a new Inbox item.

For rapid entry into Inbox without having to switch to a terminal, (assuming
you're using Linux) insure xterm is installed (since it's lightweight) and add
a shortcut key that runs the command 'xterm -e /bin/bash -c
/path/to/quick_add.py' (without quotes...change path as appropriate). -e
tells xterm to run the following command, and -c tells bash to run the
following command. This will run the command with bash even if bash isn't your
default shell. (I use zsh with OMZSH, which takes a little while to be ready
for input.) This will quickly open a window with a prompt. Add text and hit
enter, and the window will close and the text will be saved as a new Inbox
item.

quick_add.py -c will save the contents of your clipboard as a new Inbox item,
and could also be added to keyboard shortcut.

The prompt can also be used to enter multiple tasks by calling the main program
with the option -Q. Hit Ctrl-C to exit.
