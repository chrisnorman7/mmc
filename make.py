from shutil import rmtree, copytree, copy
from application import appName, appVersion, appMinorVersion
from os import system, rename, listdir, walk, path, mkdir, chdir, getcwd
import zipfile, plistlib
import sys

cwd = getcwd()

dels = [
 'dist',
 'build',
 '%s.app' % appName,
 appName
]

for d in dels:
 if d in listdir('.'):
  print 'Deleting %s...' % d
  rmtree(d)
 else:
  print 'Directory not found so not deleting: %s.' % d

if sys.platform.startswith('win'):
 system('pyinstaller -wy --clean --log-level WARN -n %s --distpath . main.py' % appName)
 output = appName
 xd = appName
elif sys.platform == 'darwin':
 system('py2applet main.py')
 n = '%s.app' % appName
 while 1:
  try:
   rename('main.app', n)
   break
  except OSError:
   continue
 output = n
 mkdir(path.join(n, 'Contents', 'Resources', 'English.lproj'))
 pf = path.join(n, 'Contents', 'Info.plist')
 p = plistlib.readPlist(pf)
 p.LSHasLocalizedDisplayName = True
 plistlib.writePlist(p, pf)
 with open(path.join(n, 'Contents', 'Resources', 'English.lproj', 'InfoPlist.strings'), 'w') as f:
  f.write('CFBundleName="%s";\nCFBundleDisplayName="%s";\n' % (appName, appName))
 xd = path.join(n, 'Contents', 'Resources')
else:
 quit("Don't know how to run on %s." % sys.platform)

if not appMinorVersion:
 print 'Adding docs.'
 chdir('docs')
 system('make html')
 chdir(cwd)
 copytree(path.join('docs', '_build', 'html'), path.join(xd, 'docs'))
else:
 print 'Not adding docs.'

for d in listdir('xtras'):
 origin = path.join('xtras', d)
 dest = path.join(xd, d)
 if path.isdir(origin):
  copytree(origin, dest)
 else:
  copy(origin, dest)
 print 'Copied %s.' % d

print 'Creating Zipfile...'
z = '%s-%s-%s.zip' % (appName, appVersion, sys.platform)
zf = zipfile.ZipFile(z, 'w')
for root, dirs, files in walk(output):
 for file in files:
  p = path.join(root, file)
  zf.write(p)
zf.close()
print 'Zip file created.'
