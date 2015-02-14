import accessible_output2.outputs.auto as ao

from sys import platform
if platform == 'darwin':
 OSX = True
 import os
 from threading import Thread
else:
 OSX = False

class System(ao.Auto):
 if OSX:
  def speak(self, *args, **kwargs):
   """Threaded speech to try and stop VoiceOver from lagging so much."""
   t = Thread(target = os.system, args = [r'osascript -e "tell application \"voiceover\" to output \"%s\"" &' % args[0].replace('"', r'\\\"')])
   t.start()
   return t

system = System()
