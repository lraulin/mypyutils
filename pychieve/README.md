For ease of use, make a short alias for pygtd. I use 'gt' (for Getting Things
Done since I've already assigned 'in' as an alias). Then type the command
followed by text to be entered. Quotes are not necessary as long as you don't
use any special characters; if no optional argument flags are used (-i, -q,
etc), all arguments will be gathered into a single string, which will be saved
as a new Inbox item.

For rapid entry into Inbox without having to switch to a terminal, insure xterm
is installed (since it's lightweight) and add a shortcut key that runs the  
command 'xterm -e /bin/bash -c /path/to/quick_add.py' (without quotes...change  
path as appropriate). -e tells xterm to run the following command, and -c tells
bash to run the following command. This will run the command with bash even if
bash isn't your default shell. (I use zsh with OMZSH, which takes a little
while to be ready for input.) This will quickly open a window with a prompt.
Add text and hit enter, and the window will close and the text will be saved
as a new Inbox item.

The prompt can also be used to enter multiple tasks by calling the main program
with the option -Q. Hit Ctrl-C to exit.

This helps with the capture portion of GTD methodology. Enter ideas whenever
they occur to you. Don't think too much...just write it down. Later, you can
process your Inbox and decide what if anything to do about it.
