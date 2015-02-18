# Programming with MMC {#programming}

This page will attempt to teach you the basics of programming with MMC.

If you do not know [Python](http://www.python.org), then it is recommended you learn that first. Python is an easy to learn language, and generally yields positive results very quickly.

We will be using version 2.7.9.

[TOC]

## Introduction {Introduction}

At the heart of MMC is the world object. As in Python, everything is an [object](https://docs.python.org/2/tutorial/classes.html), including the connected world, the user interface, and the triggers and aliases you define.

There are several ways to script in MMC, the most powerful of wich are raw Python files, which MMC refers to as [Script Files](@ref script-files), but there is a lot of stuff you can do from the entry line as well.

Let's dive right in:

### Your First Script {#FirstScript}

#### The Command Character {#CommandCharacter}

Begin your command with the Command Character, which can be configured from the entry tab of the world options window.

By default this is a / character, so your command might look like this:

    /print "Hello world."
 
If you've used Python before, you'll recognised the print statement. It usually prints stuff to the console. By default, MMC has redirected the [standard streams](http://en.wikipedia.org/wiki/Standard_streams), so any text which would usually appear on the console now appears in your output window.

This of course includes tracebacks or errors. Try this code:

    /print asdf
 
You should see the following printed to your output window:

   Traceback (most recent call last):
      File ".../gui/worldframe.py", line 189, in onEnter
    self.world.send(v)
      File ".../world.py", line 501, in send
    return self.execute(self.normalise(command[1:]))
      File ".../world.py", line 576, in execute
    eval(c, self.getEnvironment(environment))
      File "errors.log", line 1, in <module>
    NameError
    : 
    name 'asdf' is not defined

This is a long winded error. As with most pythonic errors, it's only the last line that's of interest:

    NameError
    : 
    name 'asdf' is not defined

This shows you that nothing evaluates to asdf. Let's try something that will match. Type the following:

    /print classes
 
You should see something like:

    deque([])

This is because the world object has a property named classes.

#### Entry Variables {#EntryVariables}

This method of scripting allows you to send variables with your MUD output.

Imagine you wanted to send your friend the contents of the note variable you just made. You might have set it like this:

    /world.note = 'The potion is at the house on the eastern road.'

Now instead of writing all that again, you could simply type:

    tell jo @note

MMC would send:

    tell jo The potion is at the house on the eastern road.

You can change the regular expression used for this magic in the scripting tab of world options.

If there is no variable matching your command, MMC simply sends the text verbatim.

#### Entry Expressions {#EntryExpressions}

To build upon the last section, you can also enter entire equations on the command line by enclosing them with @{}. For example:

    @{5 + 4}
 
This would make MMC send the number 9.

In short, anything between the braces is treated like a [Python Lambda](http://www.secnetix.de/olli/Python/lambda_functions.hawk), which is a fancy word for a single line of code.

Lambdas are not restricted to mathematical equations however. Consider the following code:

    /world.fruits = ['grapes', 'apples', 'oranges', 'lemons', 'bananas']
    say My favourite fruits are @{', '.join(world.fruits)}.
 
This would give you:

    say My favourite fruits are grapes, apples, oranges, lemons, bananas.
 
To make that more gramatically correct, we could do:

    say My favourite fruits are @{', '.join(world.fruits[:-1])}, and @{world.fruits[-1]}.

That would give you:

    say My favourite fruits are grapes, apples, oranges, lemons, and bananas.

You can change the regular expression used for this magic in the scripting tab of world options.

#### Script Files {#ScriptFiles}

Script files are by far the most powerful method of programming with MMC.

These files are just Python files, and are executed from inside MMC, which provides [globals](https://docs.python.org/2/library/functions.html#globals) and [locals](https://docs.python.org/2/library/functions.html#locals) which include the world object, the window (user interface) object, and the list of classes and triggers.

To have a script load each time you open your world, you need to set up your start file in the script tab of world options.

This file gets executed once your world is loaded, just before it connects.

In this way, you can instantly load triggers and aliases.

