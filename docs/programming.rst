.. highlight:: python
   :linenothreshold: 1
.. _programming:
===================
Programming with MMC
===================

This page will attempt to teach you the basics of programming with MMC.

If you do not know `Python <http://www.python.org>`_, then it is recommended you learn that first. Python is an easy to learn language, and generally yields positive results very quickly.

We will be using version 2.7.8.

.. _scripting-introduction:
===========
Introduction
===========

At the heart of MMC is :ref:`world-object`. As in `Python <http://www.python.org>`_, everything is an `object <https://docs.python.org/2/tutorial/classes.html>`_, including the connected world, :ref:`window-object`, and the :ref:`triggers <trigger-object>` and :ref:`aliases <alias-object>` you define.

Let's dive right in:

.. _first-script:
=================
Your First Script
=================

In addition to :ref:`script-files`, you can enter code on the :ref:`entry-line` of MMC. There are three ways to do this:

.. _command-character:
===================
The Command Character
===================

Begin your command with the Command Character, which can be configured from the :ref:`entry-tab` of the :ref:`world-options` window.

By default this is a / character, so your command might look like this::

 /print "Hello world."
 
If you've used Python before, you'll recognised the print statement. It usually prints stuff to the console. MMC has redirected the `standard streams <http://en.wikipedia.org/wiki/Standard_streams>`, so any text which would usually appear on the console, now appears in your output window.

This of course includes tracebacks or errors. Try this code::

 /print asdf
 
You should see the following printed to your output window::

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

This is a long winded error. As with most pythonic errors, it's only the last line that's of interest::

 NameError
 : 
 name 'asdf' is not defined

This shows you that nothing evaluates to asdf. Let's try something that will match. Type the following::

 /print classes
 
You should see something like::

 deque([])

This is because :ref:`world-object` has a property named :ref:`classes <classes-property>`.

.. _entry-variables:
=============
Entry Variables
=============

This method of scripting allows you to send variables with your MUD output.

Imagine you wanted to send your friend the contents of the note variable you just made. You might have set it like this::

 /world.note = 'The potion is at the house on the eastern road.'

Now instead of writing all that again, you could simply type::

 tell jo @note

MMC would send::

 tell jo The potion is at the house on the eastern road.

You can change the regular expression used for this magic in :ref:`scripting-tab` of :ref:`world-options`.

If there is no variable matching your command, MMC simply sends the text verbatim.

.. _entry-expressions:
===============
Entry Expressions
===============

To build upon :ref:`the last section <entry-variables>`, you can also entry entire equations on the command line by enclosing them in @{}. For example::

 @{5 + 4}
 
This would make MMC send the number 9.

In short, anything between the braces is treated like a `Python Lambda <http://www.secnetix.de/olli/Python/lambda_functions.hawk>`, which is a fancy word for a single line of code.

Lambdas are not restricted to mathematical equations however. Consider the following code::

 /world.fruits = ['grapes', 'apples', 'oranges', 'lemons', 'bananas']
 say My favourite fruits are @{', '.join(world.fruits)}.
 
This would give you::

 say My favourite fruits are grapes, apples, oranges, lemons, bananas.
 
To make that more gramatically correct, we could do::

 say My favourite fruits are @{', '.join(world.fruits[:-1])}, and @{world.fruits[-1]}.

That would give you::

 say My favourite fruits are grapes, apples, oranges, lemons, and bananas.

You can change the regular expression used for this magic in :ref:`scripting-tab` of :ref:`world-options`.

.. _script-files:
===========
Script Files
===========

Script files are by far the most powerful method of programming with MMC.

These files are just Python files, and are executed from inside MMC, which provides `globals <https://docs.python.org/2/library/functions.html#globals>`_ and `locals <https://docs.python.org/2/library/functions.html#locals>`_ such as :ref:`world-object`, and :ref:`window-object`.

To have a script load each time you open your world, you need to set up your :ref:`startfile-option` in :ref:`scripting-tab` of :ref:`world-options`.

This file gets executed once your world is loaded, just before it connects.

In this way, you can instantly load triggers and aliases.

Beware though, you cannot load hotkeys until :ref:window-object` has been assigned to the world. To work around this, simply have your keys created in response to a trigger which you know appears soon after the connections is established.

.. _scripting-advanced:
=======
Advanced
=======

For more advanced topics, read the help on the various :ref:`objects <objects>`.

