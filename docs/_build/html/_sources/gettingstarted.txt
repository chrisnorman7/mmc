.. _getting-started:

====================
Getting Started with MMC
====================

When you first load MMC you are presented with a blank window. From here you have two options:

* Create a new world.
* Open an existing world file.

If you create a new world, you are presented with the :ref:`world-options` screen, where you can enter your connection information amongst other things.

There are a lot of options, so it is highly recommended you look through them all, but to connect you only need to enter the hostname and the port, which can be found in the :ref:`entry-tab`.

When you have entered these pieces of information, click the OK button, and the window should close, returning you to your disconnected world.

If you open a world file, the world will open, and the options stored in the world file take effect.

.. _getting-connected:

====================
Getting Connected
====================

To connect your world, click on the :ref:`GUI-Connection`, and click Connect. Alternatively, you can hit CTRL+K (or CMD+K on Macintosh systems).

If you have entered your information correctly, MMC should now connect your world.

If you had loaded any script files, or there was a connection problem, an error message would show on screen alerting you to the problem.

If you wish to disconnect from the world, you can use the connection menu again, or press CTRL+SHIFT+K (CMD+SHIFT+K on Macintosh systems).

====================
The Connect String
====================

Instead of restricting your choices of how to connect, MMC gives you a fully customisable experience. Alongside the hostname and port settings in the :ref:`connection-tab`, the connect string allows you to string together any series of commands you want, seperated by the command seperator (semicolon (;) by default), which can be found in the :ref:`entry-tab`.

Using the formatters listed, construct your login string. For example, here is an example which would give you the connect string for a typical Lambda MOO installation::

 connect {u} {p}
 
This sends something like the following::

 connect john password123
 
Here is an example which will allow you to connect to most Diku-style MUDs::

 {u};{p}
 
This would send something like::

 john
 password
 
Note the command gets put to two lines.

If you play a MUD which leaves you lying on the ground when you disconnect, you might want a connect string like the following::

 {u};{p};stand
 
This would send something like the following::

 john
 password123
 stand
 
This concludes the  basic introduction to MMC. To learn more about the options available, please browse the rest of this manual.

