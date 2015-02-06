.. _GUI:

==============================
The Graphical User Interface
==============================

The graphical user interface of MMC is relatively straightforward. The application is menu-driven, resulting in an organized but tasteful representation of the options you have available to you. Each menu will be detailed here.

.. _GUI-File:

===================
File Menu
===================

The file menu contains options for manipulating or loading world files. Options are explained below.

* New:
  Opens a dialogue prompting for options to include in your new world. For more information on this, see :ref:`the section regarding world properties <world-options>`.
* Open:
  Loads a world file. Should be of type .mmcworld.
* Save/Save As:
  Save an actively open world, or save a separate copy elsewhere.
* Exit:
  Exit MMC.

.. _GUI-Send:

===================
Send Menu
===================

* Send File:
This option sends a file to the MUD. If you are not connected, nothing will happen. If you are connected, all lines of the file will be parsed as commands.

* Send log:
This will prompt you to locate an MMC-log formatted file to parse. The log parser will allow you to replay logs as if you were witnessing them in realtime. Note: files that have not been formatted for the MMC logging specification will not work.

.. _GUI-Connection:

===================
Connection Menu
===================

* Open connection:
Open a connection to the existing world. This can also be completed by pressing ctrl+K
* Close connection:
Disconnect from the active world. This can also be completed by pressing ctrl+shift+K.

.. _GUI-programming:

===================
Programming Menu
===================

* Add alias:
Add an alias to your .mmcworld file. Aliases are described 
:ref:`here <world-aliases>`.
* Edit aliases:
Edit or delete an existing alias. Aliases are described 
:ref:`here <world-aliases>`.
You can also use ctrl+shift+A as an accelerator to reach this dialogue.
* Add trigger:
Add a trigger to your .mmcworld file. Triggers are described 
:ref:`here <world-triggers>`.
* Edit triggers:
Edit or delete an existing trigger. Triggers are described
:ref:`here <world-triggers>`.
You can also use ctrl+shift+T as an accelerator to reach this dialogue.

