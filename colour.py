import re
escape = chr(27)

colourRe = re.compile(r'(%s\[([^m]+)m)' % escape)
def matchColour(text):
 location = 0
 results = []
 match = False
 for (full, code) in re.findall(colourRe, text):
  text = text.replace(full, '')
  if match:
   results.append((location, code))
  