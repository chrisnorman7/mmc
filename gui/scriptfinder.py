"""Find scripts for the games you connect too."""

import wx

class ScriptFinderFrame(wx.Frame):
 """The GUI front end for ScriptFinder."""
 def __init__(self, *args, **kwargs):
  super(ScriptFinderFrame, self).__init__(*args, **kwargs)
  