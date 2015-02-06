.. _world-object:

==================
The world object
==================

This is the world class, from which all worlds are derived. All the below functions are available to the programmer without needing to use the world.member syntax, thanks to the :func:`getEnvironment <world.World.getEnvironment>` function.

.. _world-api:

=================
The World API
=================

.. autoclass:: world.World
   :members:
.. _world-options:

==================
The World Options Dialogue
==================

The world properties dialogue features several tabs to configure your world to your liking. The tabs include world, connection, entry, output, accessibility, and many others. Each tab has it's own custom help which can be displayed by clicking on the help button. To connect to your world, you should fill out the world name on the world tab, and then add the connection info (both hostname and port) under the connection tab. If you are a blind user, you should configure your screen reader options via the accessibility tab. This section will include more detailed help pertaining to each tab soon.