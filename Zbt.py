import bluetooth


class Client:

    def __init__(self, sock=None,):
        self.sock = None

        if sock is None:
            self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        else:
            self.sock = sock

    def connect(self,host="AC:3F:A4:80:67:FD",port=1):
        self.host = host
        self.port = port

        try:
            print("Attempting Connection...")
            # Create client socket
            self.sock.connect((host, port))
        except bluetooth.btcommon.BluetoothError as error:
            print("Could not connect: ", error, "; Retrying in 5s...")


    def mysend(self):

        self.sock.send("! U1 getvar \"device.languages\"\r\n\r\n")


    def myreceive(self):
        data = self.sock.recv(32768)
        print(data)



c= Client()
c.connect()


