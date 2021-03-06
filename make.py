from shutil import rmtree, copytree, copy
from application import appName, appVersion, appMinorVersion
from os import system, rename, listdir, walk, path, mkdir, chdir, getcwd, remove
from ConfigParser import SafeConfigParser as SCP
import zipfile, plistlib, json, sys

cwd = getcwd()

dels = [
 'dist',
 'build',
 '%s.app' % appName,
 appName
]

for d in dels:
 if d in listdir('.'):
  if path.isfile(d):
   print 'Deleting %s...' % d
   remove(d)
  else:
   print 'Removing directory: %s.' % d
   rmtree(d)
 else:
  print 'Not found: %s.' % d

system('pip install -Ur requirements.txt')
if sys.platform.startswith('win'):
 system('pip install -U pyinstaller & pyinstaller -wy --clean --log-level WARN -n %s --distpath . main.py' % appName)
 try:
  remove('main.spec')
 except OSError as e:
  print 'Error: %s.' % e
 xd = appName
 output = appName
elif sys.platform == 'darwin':
 system('pip install -U py2app; py2applet main.py')
 n = '%s.app' % appName
 while 1:
  try:
   rename('main.app', n)
   break
  except OSError as e:
   pass
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
z = '%s-%s-{platform}.zip' % (appName, appVersion)

c = SCP()

zf = zipfile.ZipFile(z.format(platform = sys.platform), 'w')
for root, dirs, files in walk(output):
 for file in files:
  p = path.join(root, file)
  zf.write(p)
zf.close()
print 'Zip file created.'
if c.read('config.ini'):
 d = {
  'version': appVersion,
  'download': '%s%s' % (c.get('urls', 'download'), z)
 }
 with open('version.json', 'w') as f:
  json.dump(d, f)
 print 'Uploading Zip File...'
 hspec = '%s@%s:' % (c.get('scp', 'username'), c.get('scp', 'hostname'))
 system('scp "%s" %s%s' % (z.format(platform = sys.platform), hspec, c.get('scp', 'binary_destination')))
 system('scp version.json %s%s' % (hspec, c.get('scp', 'json_destination')))
