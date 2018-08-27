import sys
from Py3dsMax import mxs
exLibs = "C:/Python2.7.6/Lib/site-packages/"
if not exLibs in sys.path:
	sys.path.append(exLibs)
import MaxPlus
from cross3d import Scene
scene = Scene()
print scene.currentFileName()
print len(scene.objects())
for obj in scene.objects():
	MaxPlus.Core.EvalMAXScript("print %s"%obj)