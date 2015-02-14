from threading import Thread
from application import maxThreads

class MatchObject(object):
 """Will store matched results."""
 def __init__(self):
  self.results = []
  self.done = 0

def getChunks(stuff, jump = maxThreads):
 """Split stuff into maxThreads-sized chunks."""
 n = len(stuff)
 j = (n / jump) + 1
 for i in xrange(0, n, j):
  yield stuff[i:i + j]

def match(thing, source, tester):
 """Matches <item>s in <stuff> to <match>, calling tester(match, item) to ascertain a match."""
 r = MatchObject()
 for x in getChunks(source):
  Thread(target = _match, args = (thing, x, tester, r)).start()
 while r.done < maxThreads:
  pass
 return r

def _match(match, stuff, tester, thing):
 """Using tester, match in stuff, and add the results to thing."""
 for s in stuff:
  t = tester(match, s)
  if t != None:
   thing.results.append(t)
 thing.done += 1
