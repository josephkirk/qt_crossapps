#######################Server Init########################## 
import maya.utils
def runServer():
    exec(open("D:/Works/Code/Qt_crossapps/Libs/server.py").read(), globals(), locals())
maya.utils.executeDeferred(runServer)
#######################FOR VMTB,DO NOT TOUCH########################## 
