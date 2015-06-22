from uptime import uptime
import psutil

if __name__ == '__main__':
    print(int((uptime()/60)%60))
    print(psutil.users())
