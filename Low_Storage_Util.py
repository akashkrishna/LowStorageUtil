#!/usr/bin/env python
from __future__ import print_function
import subprocess as sp
import sys, os, time, ctypes

kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 128) #Locking terminal edit mode
cls = lambda: os.system('cls||clear') #To support Linux
if sys.version_info<(3,0): input=raw_input #To support Py2

def resource_path(relative_path): #Getting absolute path to resource for PyInstaller
    try:
        base_path = sys._MEIPASS #PyInstaller creates a temp folder and stores path in _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

while True:
    try:
        cls(); sp.check_output(["adb", "get-state"]) #To check number of devices connected
    except sp.CalledProcessError:
         sp.call("adb devices -l",shell=True) #Printing list of connected devices
         state = input("Please connect only one device and enable its USB debugging.\n Hit enter to retry...\n")
         continue
    else:
        cls(); n, c, tspent = 0, 25.4, 0.0

        #Getting device name and its DSN
        devices = sp.Popen("adb devices -l",stdout=sp.PIPE,stderr=sp.PIPE,shell=True); _devices = devices.stdout.read().decode('utf-8')
        list = _devices.strip().split(); dtype, dsn = list[8], list[4]

        #Getting free space available
        mem = sp.Popen("adb -s {} shell df -H /sdcard/ | grep G".format(dsn),stdout=sp.PIPE,stderr=sp.PIPE,shell=True); df = mem.stdout.read().strip().split();
        fsp=df[3]; lft=float(fsp[:-1]); ovs=df[1].decode('utf-8')

        #Creating new directory for sideloading if already exists to avoid overwriting
        exi_dir = sp.Popen("adb -s {} shell ls /sdcard/ | grep Sideloaded".format(dsn),stdout=sp.PIPE,stderr=sp.PIPE,shell=True)
        _dir = exi_dir.stdout.read().decode('utf-8'); dir_list = _dir.strip().split();
        if not dir_list:
            dir='Sideloaded'
        else:
            dir=dir_list[-1]+'1'

        print ("Sideloading multimedia files to {} {}'s emulated storage.\n Do not remove the device until execution is fully complete.\n".format(dtype,dsn))
        while "G".encode('utf-8') in fsp or lft > 300.0: #Sideloads as long as free space is in GB or until greater than 300MB (cache included)
            try:
                start_time=time.time()
                sp.check_call("adb -s {} push {} /sdcard/{}/Video_{}.mp4".format(dsn,resource_path('src/Video.mp4'),dir,n),shell=True)
                sp.check_call("adb -s {} push {} /sdcard/{}/Audio_{}.mp3".format(dsn,resource_path('src/Audio.mp3'),dir,n),shell=True)
                sp.check_call("adb -s {} push {} /sdcard/{}/Image_{}.jpg".format(dsn,resource_path('src/Image.jpg'),dir,n),shell=True)
                sp.check_call("adb -s {} push {} /sdcard/{}/Document_{}.doc".format(dsn,resource_path('src/Document.doc'),dir,n),shell=True)
                end_time=time.time()-start_time
            except sp.CalledProcessError:
                cpe = input ("\n Above error occured. Rerun the program to sideload more.\n Hit Enter to exit.")
                break
            except KeyboardInterrupt:
                q = input("\n\n\tCancel sideloading...? Y/N: ")
                if q.upper() == 'Y':
                    print ("Sideloading cancelled!"); break
                else:
                    continue
            else:
                tspent+=end_time; speed=round(c/tspent,2);
                if 'G'.encode('utf-8') in fsp:
                    estimated=lft*1000/speed
                else:
                    estimated=lft/speed
                elapsed, eta = round(tspent/60,2), round(estimated/60,2)
                cls(); print("Elapsed: {} Mins \tSpeed: ~{} MB/s \tETA: {} Mins".format(elapsed,speed,eta))

                #Updating storage details
                mem = sp.Popen("adb -s {} shell df -H /sdcard/ | grep G".format(dsn),stdout=sp.PIPE,stderr=sp.PIPE,shell=True); df = mem.stdout.read().strip().split()
                fsp=df[3]; lft=float(fsp[:-1]); prc=df[4].decode('utf-8'); usd=df[2].decode('utf-8')
                if '%' not in prc: prc=str(int(round(float(usd[:-1])/float(ovs[:-1])*100)))+'%'

                print ("\nSideloaded: {} GB ({} files)\t Free: ~{}B\t Used: {}B/{}B ({})\n\n       Do not remove {} {}\n".format(round(c/1000,2),(n+1)*4,fsp.decode('utf-8'),usd,ovs,prc,dtype,dsn))
                print('-'*100+'\n'); n+=1; c+=25.4

        else:
            cls();
            print("\nSideloading completed. Minimum free space of ~150MB left in the device storage.\nOverall storage details including cache:\n")
            sp.call("adb -s {} shell df -H /sdcard/".format(dsn),shell=True)
            ext = input("\n Hit Enter to exit...")
            break
        break
