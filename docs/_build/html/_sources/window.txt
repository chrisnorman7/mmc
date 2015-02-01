.. _window-object:

=================
The Window Object
=================

The window object will show up to your scripts as window once it has been initialised.

It is not stored as a property of world, but instead if spliced in using the world.environment dictionary.

There are a host of useful shortcut keys, or accelerators bound to the window. You can easily override these with successive calls to AddAccelerator, in the form::

 window.AddAccelerator(modifiers, key, function)
 
Unlike the standard wx Frame, MMC's window object will happily modify accelerators on the fly.

=================
**Warning!!!**
=================

Buggy code can leave you unable to connect to your world, so be warey when manipulating this object.

.. _window-api:

=================
The Window API
=================

.. automodule:: gui.worldframe
   :members:
