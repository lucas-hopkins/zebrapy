#!/usr/bin/env/python
from datetime import datetime
import binascii
import usb.core
import usb.util
import codecs
import sys
import time

#EP_IN = 0x81
#EP_OUT = 0x01

dev = usb.core.find(idVendor=0xa5f, idProduct=0x0f3)

def connect_to_printer():
    #was the device found
    if dev is None:
        raise ValueError('Device not found')
    if dev.is_kernel_driver_active(0):
        print("Detaching kernel driver")
        reattach = True
        dev.detach_kernel_driver(0)

#### show config / interface / endpoints:
    
    #for config in dev:
    #    sys.stdout.write('Config ' + str(config.bConfigurationValue) + '\n')
    #for interface in config:
    #    sys.stdout.write('\t' + \
    #        'Interface ' + str(interface.bInterfaceNumber) + \
    #                     ',' + \
    #                     str(interface.bAlternateSetting) + \
    #                     '\n')
    #    for endpoint in interface:
    #        sys.stdout.write('\t\t' + \
    #                        'Endpoint ' + str(endpoint.bEndpointAddress) + \
    #                         '\n')
    
    
    dev.set_configuration()

    # get an endpoint instance
    cfg = dev.get_active_configuration()
    intf= cfg[(0,0)]

    epo = usb.util.find_descriptor(intf,
    # match the first OUT endpoint
        custom_match = \
        lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_OUT)
    #print(epo)

    #match the first IN endpoint
    epi = usb.util.find_descriptor(intf,
            custom_match = \
            lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_IN)
    #print(epi)

# Write to the Printer
def send_command(cmd_name, cmd_string):
        print("\ncmd_name:", cmd_name)
        print("\ncmd_string:", cmd_string)
        cmd_bytes = bytearray(cmd_string.encode('utf-8'))
        for cmd_byte in cmd_bytes:
            hex_byte = ("{0:02x}".format(cmd_byte)) 
        #hex_bytes = cmd_bytes.hex()
            dev.write(1, bytearray.fromhex(hex_byte))
            
        time.sleep(1.0)

        #print time for debugging
        t = datetime.utcnow()
        print(t)

        #read the response

def read_response():
       try:
           for x in range (0, 3):
              ret = dev.read(0x81, 64, 5000)
              print("response: ", binascii.hexlify(bytearray(ret)))
              ret =str(ret, 'utf-8')
              print(ret)
              usb.util.dispose_resources(dev)
       except usb.core.USBError as e:
            print(e)
        # This is needed to release interface, otherwise attach_kernel_driver fails
        # due to "Resource busy"


def main():

    cmd_name ='get_ip'
    cmd_string ='! U1 getvar "ip.addr" ""\r\n'
    connect_to_printer()
    send_command(cmd_name, cmd_string)
    read_response()
    dev.reset()
main()
# It may raise USBError if there's e.g. no kernel driver loaded at all
#if reattach:
#    dev.attach_kernel_driver(0)
