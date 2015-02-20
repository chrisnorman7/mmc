#!/usr/bin/python
if __name__ == '__main__':
 import application, wx, gui.worldframe, gui.updateframe
 u = gui.updateframe.UpdateFrame()
 gui.worldframe.WorldFrame()
 application.app.MainLoop()
