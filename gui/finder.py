"""Find strings in other strings with regular expressions."""

import re

class MyStr(str):
 """A string with a match routine."""
 def match(self, what):
  """Is what in this string?"""
  return self in what

def find(what, where, regexp = True, reverse = True):
 """
 find(what, where[, regexp[, reverse]])
 
 Find what in where. Returns a list of (line number, string) tuples.
 
 * what is a string or regular expression to find in where.
 * where is a list of strings to search through.
 * regexp tells find if what is a regular expression or not.
 * reverse tells find whether or not to search backward through where.
 
 """
 if type(where) != list:
  raise ValueError('where must be a list of strings.')
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
