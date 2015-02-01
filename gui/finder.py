import re

class MyStr(str):
 def match(self, what):
  return self in what

def find(what, where, regexp = True, reverse = True):
 if reverse:
  where.reverse()
 if regexp:
  what = re.compile(what)
 else:
  what = MyStr(what)
 results = []
 i = 0
 for w in where:
  if what.match(w):
   results.append((i, w))
  i += 1
 return results
