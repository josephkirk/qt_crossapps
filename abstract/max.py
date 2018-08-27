import subprocess
import shlex
import time
def runServer():
    command = "D:/Env/Continuum/miniconda2/python D:/Works/Code/Qt_crossapps/samples/client_server/reply.py"
    while True:
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        output = process.stdout.readline()
        if output == '':
            process.terminate()
            time.sleep(5)
            #break
        else:
            print(output.strip())
runServer()