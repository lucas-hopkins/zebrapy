
from usb import core
import usb.util
import usb
import sys

command ="^XA^FO20,20^A0N,25,25^FDThis is a ZPL test.^FS^XZ"
dev = usb.core.find(idVendor=0xa5f, idProduct=0x0f3)
if dev is None:
     raise ValueError('Device not found')
dev.set_configuration()

 #Find endpoints
ep_out = usb.util.find_descriptor(
         dev.get_interface_altsetting(),   # first interface
        # match the first OUT endpoint
         custom_match = \
             lambda e: \
                 usb.util.endpoint_direction(e.bEndpointAddress) == \
                 usb.util.ENDPOINT_OUT
     )

ep_in = usb.util.find_descriptor(
         dev.get_interface_altsetting(),   # first interface
         # match the first OUT endpoint
         custom_match = \
             lambda e: \
                 usb.util.endpoint_direction(e.bEndpointAddress) == \
                 usb.util.ENDPOINT_IN
     )

a=ep_out.write(command)
ret=ep_in.read(64, timeout=12000)
print ret
