LOG_MODE = 'FUCK'

# define a file for logging ...
WORK_FOLDER = r"C:\Users\reeddotaer\Desktop\clgzwqcode\new_adp\log/"
DEBUG_LOGFILE = 'mylog'
# ...and clear it initially
if LOG_MODE == 'FILE':
    with open(WORK_FOLDER + DEBUG_LOGFILE,"w") as f:
        pass
# define a function for writing messages to the file
def logDebug(msg):
    if LOG_MODE == 'FILE':
        with open(WORK_FOLDER + DEBUG_LOGFILE,"a") as f:
            f.write(str(msg)+"\n")
            f.flush()
    elif LOG_MODE == 'PRINT':
        print(msg)
    else:
        pass

# define a function to get exception traceback
def logTraceBack():
    import traceback
    if LOG_MODE == 'FILE':
        with open(WORK_FOLDER + DEBUG_LOGFILE,"a") as f:
            traceback.print_exc(file=f)
            f.flush()
    elif LOG_MODE == 'PRINT':
        traceback.print_exc()
    else:
        pass