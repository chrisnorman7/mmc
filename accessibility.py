import accessible_output2.outputs.auto as ao

class System(ao.Auto):
 def speak(self, *args):
  speak = self.get_first_available_output()
  if hasattr(speak, 'speak'):
   speak.speak(*args)
   return True
  else:
   return False
 
 def braille(self, *args):
  braille = self.get_first_available_output()
  if hasattr(braille, 'braille'):
   braille.braille(*args)
   return True
  else:
   return False
 
 def silence(self):
  f = self.get_first_available_output()
  if hasattr(f, 'silence'):
   f.silence()
   return True
  else:
   return False

system = System()
