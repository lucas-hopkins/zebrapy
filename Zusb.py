import usb.core
import usb.util
import usb.control
import json


dev = usb.core.find(idVendor=0xa5f)

if dev is None:
    raise ValueError('Device not found')

if dev.is_kernel_driver_active(0):
    reattach = True
    dev.detach_kernel_driver(0)
# set the active configuration. With no arguments, the first
# configuration will be the active one
dev.set_configuration()

# get an endpoint instance
cfg = dev.get_active_configuration()
intf = cfg[(0,0)]

ep = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_OUT)

assert ep is not None

# write the data
msg = '\n! U1 getvar "comm.baud"\n'
dev.write(ep.bEndpointAddress, msg.encode('ascii'), ep.wMaxPacketSize)

# read the data
data = dev.read(ep.bEndpointAddress, ep.wMaxPacketSize)
datar = ''.join([chr(x) for x in data])
print(datar)

# remove lock on USBcd
usb.util.dispose_resources(dev)


