
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

import usb.core
import usb.util
from pyfiglet import Figlet


class zebraPrinter:

    def __init__(self, dev):  # define the constructor

        self.dev = dev
        self.cmd_strings = ''
        self.intf = None

    def get_printer(self):

        try:
         # find all printers with the Zebra id (This supposes there is only
         # one)
            self.dev = usb.core.find(idVendor=0xa5f)
            # if self.dev is None:
            if self.dev.is_kernel_driver_active(0):
                print("Detaching kernel driver")
                reattach = True
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

    # Write to the Printer
    # def get_file(self):  --------------------- Implement later
    # def get_commands_from_file(self): --------------------- Implement later

    def format_commands(self,cmd):

        print("\ncmd_string:", cmd)
        cmd_bytes = bytearray(cmd.encode('utf-8'))
        result = ''
        for cmd_byte in cmd_bytes:
            hex_byte = ("{0:02x}".format(cmd_byte))
            result += hex_byte
            # hex_bytes = cmd_bytes.hex()
        return result
    
    def send_to_printer(self, result):
        epo = self.get_out_endpoints()
        print("Sending...")
        self.dev.write(epo, bytearray.fromhex(result))
            
        #time.sleep(1)
            #self.dev.write(
            #    self.get_out_endpoints(),
            #    bytearray(0))
            # print time for debugging
        t = datetime.utcnow()
        print(t)

    def read_response(self):
        try:
            epi = self. get_in_endpoints()
            ret = self.dev.read(epi, 64)
            r = ret.join()
            print (r)

            print("response: ", binascii.hexlify(bytearray(r)))
            ret = str(r, 'utf-8')
            print(r)
        except usb.core.USBError as e:
            print(e)

    def dispose(self):
        
        usb.util.dispose_resources(self.dev)
        self.dev = None


class menuHandler():

    def menu(self):
        f = Figlet(font='standard', width=440)
        print(f.renderText('42Q Configurator'))

        for x in range(0, 3):
            print('\n')

        print('Enter an option: ')
        print('(c) - command list')
        print('(u) - send commands over USB')
        print('(i) - send commands over TCP/IP')

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

def main():

    
    m = menuHandler()
    dev = ''
    z = zebraPrinter(dev)
    
    print("\n" * 50)
    m.menu()
    choice = m.getChoice()
    if choice == 'c':
        m.help_page()
    if choice == 'u':
        z.get_printer()
        z.set_configuration()
        cout = z.get_out_endpoints()
        print(cout)
        cin = z.get_in_endpoints()
        print(cin)
        print("\n" * 50)
        print(" Enter command(s) or press \'q\' to quit" + '\r\n')
        print(
            "Once all the desired commands are entered, press Ctrl + D to submit" +
            '\r\n')
        print("Format: ! U1 setvar/getvar \"ip.addr\"")
        cmds = []
        while True:
            try:
                cmd = input()
                cmds.append(cmd)
                #c = cmds
                print(cmds)
            except EOFError:
                break
      
        for cmd in cmds:

            r = z.format_commands(cmd)
            z.send_to_printer(r) 
        
        try:
            z.read_response()
            if z.read_response() is None:
                z.dispose()
        except usb.core.USBError:
            print('Bad')
        print("Select (r) to return the command option or (m) for the main menu")
        choice = input()
        if choice == 'm':
            print("\n" * 100)
            m.menu()
            m.getChoice()
    else:
        print("Sorry....Nope")
        m.getChoice()



if __name__ == '__main__':
    main()
