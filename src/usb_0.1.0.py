#!/home/lucas/.virtualenvs/usb_dev/bin/python3

# Test Commands

#! U1 getvar "ip.addr" ""


from datetime import datetime
# import argparse -------------Eventually implement for accessing
# functionality directly
import binascii
import sys
# import codecs
# from colorama import init  - For Figlet color support
# init(strip=not sys.stdout.isatty())
# from termcolor import cprint - For Windows color support
from pyfiglet import Figlet
import time
import subprocess
import usb.core
import usb.util


class zebraPrinter:


    def __init__(self):  # define the constructor

        self.dev = None  
        self.cmd_strings = []
        cmd_strings = self.cmd_strings
        # self.set_configuration()
        # self.get_out_endpoints()
        # self.get_in_endpoints()
        # self.get_commands()
        # self.send_to_printer()
        # self.read_response()

    def get_printer(self):
        
        try:
            dev = self.dev
            # find all printers with the Zebra id (This supposes there is only one)
            dev = usb.core.find(idVendor=0xa5f)
            # was the device found
            if self.dev is None:
                except ValueError as e 
                print('Device not found')
                print("Please plug in the printer")
            if self.dev.is_kernel_driver_active(0):
                print("Detaching kernel driver")
                reattach = True
                self.dev.detach_kernel_driver(0)


#### show config / interface / endpoints: ################################
    # for config in dev:
    #    sys.stdout.write('Config ' + str(config.bConfigurationValue) + '\n')
    # for interface in config:
    #    sys.stdout.write('\t' + \
    #        'Interface ' + str(interface.bInterfaceNumber) + \
    #                     ',' + \
    #                     str(interface.bAlternateSetting) + \
    #                     '\n')
    #    for endpoint in interface:
    #        sys.stdout.write('\t\t' + \
    #                        'Endpoint ' + str(endpoint.bEndpointAddress) + \
    #                         '\n')
###########################################################################

    def set_configuration(self):

        self.dev.set_configuration()
        # get an endpoint instance
        cfg = self.dev.get_active_configuration()
        self.intf = cfg[(0, 0)]

        return self.intf

    def get_in_endpoints(self):

        epo = usb.util.find_descriptor(
            self.intf,
            # match the first OUT endpoint
            custom_match=lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_OUT)
        # print(epo)
        return epo

    def get_out_endpoints(self):
        # match the first IN endpoint
        epi = usb.util.find_descriptor(
            self.intf,
            custom_match=lambda e:
            usb.util.endpoint_direction(e.bEndpointAddress) ==
            usb.util.ENDPOINT_IN)
        # print(epi)
        return epi

    # Write to the Printer
    def get_commands(self): # --------------------Work here ------------ Not finished. Need to update for multiline input

        print(" Enter command(s) or press \'q\' to quit" + '\r\n')
        print("Once all the desired commands are entered, press Ctrl + D to submit")
        
        while True:
            try:
                self.cmd_strings = []
                cmd_string = input()
                if cmd_string == 'q':
                    sys.exit()
                elif cmd_string == '\r':
                    continue
                elif cmd_string == '':
                    continue
                else:
                    self.cmd_strings = self.cmd_strings.append(cmd_string)
                    continue
            except EOFError:
                yield self.cmd_strings

    # def get_file(self):               --------------------- Implement later
    # def get_commands_from_file(self): --------------------- Implement later

    def send_to_printer(self, cmd_strings):
        cmd_strings = self.get_commands()
        for cmd_string in cmd_strings:
            cmd_string = (cmd_string + '\r\n')
            print("\ncmd_string:", cmd_string)
            cmd_bytes = bytearray(cmd_string.encode('utf-8'))
            for cmd_byte in cmd_bytes:
                hex_byte = ("{0:02x}".format(cmd_byte))
            # hex_bytes = cmd_bytes.hex()
                self.dev.write(1, bytearray.fromhex(hex_byte))
                time.sleep(1.0)

            # print time for debugging
            t = datetime.utcnow()
            print(t)

 # read the response

    def read_response(self):
        try:
            for x in range(0, 1):  # remove as it serves no purpose
                while 1:
                    ret = self.dev.read(self.get_in_endpoints(), 1024, 5000)
                    print("response: ", binascii.hexlify(bytearray(ret)))
                    ret = str(ret, 'utf-8')
                    print(ret)
                    usb.util.dispose_resources(self.dev)
        except usb.core.USBError as e:
            print(e)
        # This is needed to release interface, otherwise attach_kernel_driver fails
        # due to "Resource busy"


class menuHandler():

    def menu(self):
        f = Figlet(font='standard', width=1920)
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
        f = Figlet(font='standard', width=1920)
        print(f.renderText('Help'))

        for x in range(0, 3):
            print('\n')

        f = open('help.txt')
        print(f.read())
        f.close()

        
        while True:
            print("Press 'r' to return to the menu or 'q' to quit")
            i = input()
            if i == 'r':
                main()
            #elif i == '\r':
            #    i = input()
            elif i == 'q':
                sys.exit()
            else:
                print("I'm sorry that's not a valid option")
            # i = input()


def main():
    m = menuHandler()
    z = zebraPrinter()

    while True:
        m.menu()
        choice = m.getChoice()
        if choice == 'c':
            m.help_page()
        if choice == 'u':
            z.get_printer()
            z.set_configuration()
            z.get_out_endpoints()
            z.get_in_endpoints()
            # z.get_commands()
            z.send_to_printer(z.get_commands)
            z.read_response()
        else:
            print('Feature not implemented - Check back soon')


if __name__ == '__main__':
    main()
# It may raise USBError if there's e.g. no kernel driver loaded at all
# if reattach:
# dev.attach_kernel_driver(0)
