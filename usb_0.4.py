"""This script allows you to communicate with a Zebra printer over USB or TCP/IP"""
import socket
import binascii
import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from tkinter import *
from tkinter.filedialog import askopenfilename
import usb.core
import usb.util
from pyfiglet import Figlet


class zebraPrinter:

    def __init__(self, dev):  # define the constructor

        self.dev = dev
        self.intf = None

    def get_printer(self):

        try:
         # find all printers with the Zebra id (This supposes there is only
         # one)
            self.dev = usb.core.find(idVendor=0xa5f)
            self.dev.reset()
            # if self.dev is None:
            if self.dev.is_kernel_driver_active(0):
                print("Detaching kernel driver")
                self.dev.detach_kernel_driver(0)
        except ValueError:
            print('Device not found')

    def set_configuration(self):

        self.dev.set_configuration()
        cfg = self.dev.get_active_configuration()
        self.intf = cfg[(0, 0)]
        return self.intf

    def get_out_endpoints(self):

        epo = usb.util.find_descriptor(
            self.intf,
            custom_match=lambda e:
            usb.util.endpoint_direction(e.bEndpointAddress) ==
            usb.util.ENDPOINT_OUT)
        return epo

    def get_in_endpoints(self):
        epi = usb.util.find_descriptor(
            self.intf,
            custom_match=lambda e:
            usb.util.endpoint_direction(e.bEndpointAddress) ==
            usb.util.ENDPOINT_IN)
        return epi

    def format_commands(self,cmd):

        print("\ncmd_string:", cmd)
        cmd_bytes = bytearray(cmd.encode('utf-8'))
        result = ''
        for cmd_byte in cmd_bytes:
            hex_byte = ("{0:02x}".format(cmd_byte))
            result += hex_byte
        return result

    def command_loop(self):
        
        cmds = []
        while True:
            try:
                cmd = input()
                cmds.append(cmd)
                print(cmds)
            except EOFError:
                return cmds
    
    def send_to_printer(self, result):
        epo = self.get_out_endpoints()
        print("Sending...")
        self.dev.write(epo, bytearray.fromhex(result))
        t = datetime.utcnow()
        print(t)

    def read_response(self):
            
            try: 
                epi = self. get_in_endpoints()    
                for i in range (0, 7):            #This is really for long responses...unfortunately it doesn't seem to work correctly.
                #print("response: ", binascii.hexlify(bytearray(ret)))
                #ret = bytearray(ret, 'utf-8')
                    ret = self.dev.read(epi, epi.wMaxPacketSize)
                    ret = bytearray(ret).decode()
                    print(ret)
            except usb.core.USBError as e:
                print(e)


    def iter_cmds_loop(self, cmds):
        
        for cmd in cmds:
            r = self.format_commands(cmd)
            self.send_to_printer(r)
            self.read_response()
        self.dispose()

    def dispose(self):
        usb.util.dispose_resources(self.dev)
        self.dev = None


def file_reader():
    root = Tk()
    filename = askopenfilename(filetypes=[("Text files","*.txt")])
    root.destroy()
    with open(filename) as f: 
        cmds = f.readlines()
        cmds = [x.strip() for x in cmds]
    return cmds


class mysocket:
    '''demonstration class only
      - coded for clarity, not efficiency
    '''

    def __init__(self, sock=None):
        self.send_chunks = []
        self.chunks = []
        self.chunk = None
        self.msgsize = 0
        self.args = 87
        self.totalsent = 0
        self.submesg = None
        self.sent = 0
        self.bytessent = 0
        self.f = None
        self.MSGLEN = None
        self.msglgth = 0
        self.f = None
        self.sock = None

        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port, args=None):
        self.sock.connect((host, port))
        if args is not None :
            self.args = args

    def mysend(self, msg):

        self.submsg = (str(self.args) + ',').encode()
        self.sent = self.sock.send(self.submsg)
        self.totalsent = self.totalsent + len(self.submsg)
        self.send_chunks.append(self.submsg)

        #msg = "".join(i for i in msg if i not in "\/:*?<>|")

        self.msgsize = 0
        try:
            #self.submsg = self.f.read(random.randint(1,32768))
            self.submsg = msg.encode()
            #print ('msg=%s' % self.submsg)
            #self.submsg = self.f.read(random.randint(1,2048))
            #self.submsg = self.f.read(32768)
            while len(self.submsg) != 0:
                self.bytessent = 0
                self.msglgth = len(self.submsg)
                #print ('len(self.submsg) = %d' % self.msglgth)
                while self.bytessent < self.msglgth :
                    self.sent = self.sock.send(self.submsg[self.bytessent:])
                    if self.sent == 0:
                        #raise RuntimeError("socket connection broken")
                        self.msgsize = self.totalsent
                        break
                    self.bytessent = self.bytessent + self.sent
                    self.totalsent = self.totalsent + self.sent
                if self.bytessent == self.msglgth :
                    #time.sleep(random.randint(1,3));
                    self.send_chunks.append(self.submsg)
                    #self.submsg = self.f.read(2048)
                    #self.submsg = self.f.read(random.randint(1,32768))
                    self.submsg = self.f.read(32768)
                    #self.submsg = self.f.read(random.randint(1,2048))
                else :
                    self.send_chunks.append(self.submsg[(self.totalsent - self.bytessent):self.bytessent])
                    break

                #if (totalsent > 50000) :
                #    break   # to cut short the reads above

                #break   # to cut short the reads above

            self.sock.shutdown(self.sock.SHUT_WR)
        except Exception as e:
            print(e)
        finally:
            #print ('c :(%r) totalsent=%d\n' % (self.args, self.totalsent))
            #sys.exit(0)
            self.msgsize = self.totalsent
            return str(b''.join(self.send_chunks))

    def myreceive(self):
        #print ('self.msgsize=%d\n' % self.msgsize)
        #sys.exit(1)
        #s = []
        self.chunks = []
        try :
            self.totalbytes = 0
            #while self.msgsize > self.totalbytes :
            while True :
                self.chunk = self.sock.recv(32768)

                if not self.chunk :
                    # resource temporarily unavailable
                    #print ('returning resource unavailable')
                    #return ''.join(self.chunks)
                    return self.chunks
                elif len(self.chunk) == 0 :
                    #  EOF
                    #print ('returning EOF')
                    #return ''.join(self.chunks)
                    return self.chunks

                self.chunks.append(self.chunk)
                self.totalbytes = self.totalbytes + len(self.chunk)

                #print ('len of self.chunk = %d' % len(self.chunk))
                if (not self.chunk.endswith(b'"')):
                    continue

                # for zebra test
                s = b''.join(self.chunks)
                #print (s)
                return s.decode()

                #print ('client self.msgsize=%d, totalbytes=%d\n' % (self.msgsize, self.totalbytes))
        except Exception as e :
            print(e)
        finally :
            #print ('returning at finally')
            return (b''.join(self.chunks)).decode()

class menuHandler():

    def menu(self):
        f = Figlet(font='standard', width=440)
        print(f.renderText('Configurator'))

        for x in range(0, 3):
            print('\n')
        print('In order to use USB, you must run this script as sudo')
        print('Enter an option: ')
        print('(c) - command list')
        print('(u) - send commands over USB')
        print('(i) - send commands over TCP/IP ------Not working -_-') 
        print('(o) - open commands file')

    def getChoice(self):

        i = input()
        return i

    def help_page(self):

        subprocess.call(["vi", "-R", "help.txt"])

        while True:
            print("Press 'r' to return to the menu or 'q' to quit")
            i = input()
            if i == 'r':
                main()
            elif i == 'q':
                sys.exit()
            else:
                print("I'm sorry that's not a valid option")

    def command_menu(self):
        print("\n" * 50)
        print(" Enter command(s) or press \'q\' to quit" + '\r\n')
        print(
            "Once all the desired commands are entered, press Ctrl + D to submit" +
            '\r\n')
        print("Format: ! U1 setvar \"ip.addr\"")
    
def main():
    
    m = menuHandler()
    #dev = ''                        
    #z = zebraPrinter(dev)          # Instantiate the Printer Object
    #z.get_printer()                # Claim the Printer -> Resolve dev to the printer
    #z.set_configuration()          # Claim the intf
    #s = mysocket()
    print("\n" * 50)
    m.menu()
    choice = m.getChoice()
    if choice == 'c':
        m.help_page()
    if choice == 'u':
        dev = ''                        
        z = zebraPrinter(dev)          
        z.get_printer()                
        z.set_configuration()
        m.command_menu()
        cmds = z.command_loop()
        z.iter_cmds_loop(cmds)
    if choice == 'i':
        s = mysocket()
        print("Enter the printer IP & Port in the following format - 192.168.1.1.8080")
        connection = input()
        connection.split(':')
        host = connection[0]
        port = connection[1]
        s.connect(host, port)
        msg = input()
        s.mysend(msg)
        m = s.myreceive()
        print(m)
    if choice == "o":
            dev = ''                        
            z = zebraPrinter(dev)          
            z.get_printer()                
            z.set_configuration()
            cmds = file_reader()
            print(cmds)
            z.iter_cmds_loop(cmds)                  
    print("Select (r) to return the command option or (m) for the main menu")
    choice = input()
    if choice == 'm':
        print("\n" * 100)
        m.menu()
        m.getChoice()
    elif choice == 'r':
         m.command_menu()
         z.get_printer()
         z.set_configuration
         cmds = z.command_loop()
         z.iter_cmds_loop(cmds)
         
    else:
        print("Sorry....Nope")
        m.getChoice()

if __name__ == '__main__':
    while True:
        main()
