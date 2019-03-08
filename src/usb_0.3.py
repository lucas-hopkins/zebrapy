
"""This script allows you to communicate with a Zebra printer over USB or TCP/IP"""
# import argparse -------------Eventually implement for accessing
# functionality directly
import binascii
import logging
import os
#import queue
import subprocess
import sys
import threading
# import codecs
# from colorama import init  - For Figlet color support
# init(strip=not sys.stdout.isatty())
# from termcolor import cprint - For Windows color support
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
            ret = self.dev.read(epi, epi.wMaxPacketSize)
            print("response: ", binascii.hexlify(bytearray(ret)))
            ret = str(ret, 'utf-8')
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

class menuHandler():

    def menu(self):
        f = Figlet(font='standard', width=440)
        print(f.renderText('42Q Configurator'))

        for x in range(0, 3):
            print('\n')

        print('Enter an option: ')
        print('(c) - command list')
        print('(u) - send commands over USB')
        print('(i) - send commands over TCP/IP ------Not implemented -_-') 
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
    # This is messy.....just deal with it.

    # Instantiate a menu Object
    # Instatiate a printer Object
    
    m = menuHandler()
    dev = ''                        
    z = zebraPrinter(dev)          # Instantiate the Printer Object
    z.get_printer()                # Claim the Printer -> Resolve dev to the printer
    z.set_configuration()          # Claim the intf

        
    # Get decision at main screen
    print("\n" * 50)
    m.menu()
    choice = m.getChoice()
    if choice == 'c':
        m.help_page()
    if choice == 'u':
        m.command_menu()
        
        
        
        #cmds = []
        #while True:
        #    try:
        #        cmd = input()
        #        cmds.append(cmd)
        #        print(cmds)
        #    except EOFError:
        #        break
    
        cmds = z.command_loop()
        z.iter_cmds_loop(cmds)

    if choice == "o":
            cmds = file_reader()
            print(cmds)
            z.iter_cmds_loop(cmds)              
    
    
    
    #for cmd in cmds:
    #    r = z.format_commands(cmd)
    #    z.send_to_printer(r)
    #    z.read_response()
    #z.dispose()
        
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
