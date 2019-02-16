#!/home/lucas/.virtualenvs/usb_dev/bin/python3

"""This script allows you to communicate with a Zebra printer over USB or TCP/IP"""

from datetime import datetime
# import argparse -------------Eventually implement for accessing
# functionality directly
import binascii
import threading
import queue
import sys
# import codecs
# from colorama import init  - For Figlet color support
# init(strip=not sys.stdout.isatty())
# from termcolor import cprint - For Windows color support
import time
import subprocess
from pyfiglet import Figlet
import usb.core
import usb.util


class zebraPrinter:

    def __init__(self, dev):  # define the constructor

        self.dev = dev
        self.cmd_strings = ''
        #cmd_strings = self.cmd_strings

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

    def send_to_printer(self, cmd):
        print("Sending....")
        print(cmd)
        cmds = (cmd + '\r\n')
        print("\ncmd_string:", cmds)
        cmd_bytes = bytearray(cmds.encode('utf-8'))
        for cmd_byte in cmd_bytes:
            hex_byte = ("{0:02x}".format(cmd_byte))
            # hex_bytes = cmd_bytes.hex()
            self.dev.write(
                self.get_out_endpoints(),
                bytearray.fromhex(hex_byte))
            time.sleep(2.0)

            # print time for debugging
        t = datetime.utcnow()
        print(t)

 # read the response

    def read_response(self):
        try:
            for x in range(0, 1):  # remove as it serves no purpose
                while True:
                    ret = self.dev.read(self.get_in_endpoints(), 1024, 5000)
                    print("response: ", binascii.hexlify(bytearray(ret)))
                    ret = str(ret, 'utf-8')
                    print(ret)
                    usb.util.dispose_resources(self.dev)
        except usb.core.USBError as e:
            print(e)

#    def worker(self, in_q, out_q):
#        abort = False
#        while not abort:
#            try:
#                task = in_q.get(True, .5)
#            except Queue.Empty:
#                abort = True
#            else:
#                response = task
#                out_q.put(response)
#                in_q.task_done()


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
    dev = None
    z = zebraPrinter(dev)

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
        print(" Enter command(s) or press \'q\' to quit" + '\r\n')
        print(
            "Once all the desired commands are entered, press Ctrl + D to submit" +
            '\r\n')
        cmds = []
        while True:
            try:
                cmd = input()
                cmds.append(cmd)
                c = cmds
                print(cmds)
            except EOFError:
                break

        for cmd in cmds:
            t = threading.Thread(name='send_to_printer', target=z.send_to_printer(cmd))
            t.start()
            #z.send_to_printer(cmd)
            t2 = threading.Thread(name='read', target=z.read_response())
            t2.start()
        # print(" Select an option") -------------------------Return loop to
        # menu
        usb.util.dispose_resources(dev)
    else:
        print('Feature not implemented - Check back soon')


if __name__ == '__main__':
    main()
