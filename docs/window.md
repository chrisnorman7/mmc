# The Window Object

The window object will show up to your scripts as window once it has been initialised.

It is not stored as a property of world, but instead if spliced in using the world.environment dictionary and as such shows up in globals, both on the command line, and for use in your scripts.

There are a host of useful shortcut keys, or accelerators bound to the window. You can easily override these with successive calls to `AddAccelerator`, in the form

    window.AddAccelerator(modifiers, key, function)
 
Unlike the standard wx Frame, MMC's window object will happily modify accelerators on the fly.

