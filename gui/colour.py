import wx, re

escape = chr(27)
colourRe = re.compile(r'(%s\[([^m]+)m)' % escape)

