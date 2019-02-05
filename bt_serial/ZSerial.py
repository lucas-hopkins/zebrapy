import serial

ser = serial.Serial('/dev/usb/lp0')
print(ser.name)
ser.write('~WC')
ser.close()