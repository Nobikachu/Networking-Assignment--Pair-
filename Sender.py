import sys, socket
from Packet import Packet

class Sender:
    localhost = "127.0.0.1"
    bufferSize = 1024
    
    def __init__(self):
        """
        Initializes the sender class and reads 4 command line arguments.
        Input port, outputPort, channel input port and file to send
        """
        self.sIn = int(sys.argv[1])
        self.sOut = int(sys.argv[2])
        self.chanSocket = int(sys.argv[3])
        self.sendFile = str(sys.argv[4])
        if (self.checkRange(self.sIn) and self.checkRange(self.sOut)) != True:
            sys.exit("Either a Port is out of range or the specified file does not exist. Please try again.")
        else: 
            print("Preparing sockets:\nInput: {}\nOutput: {}\nChannel: {}\nTo send file: {}").format(self.sIn, self.sOut, self.chanSocket, self.sendFile)
        self.socketIn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketOut = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketIn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.socketOut.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.socketIn.bind((self.localhost, self.sIn))
        self.socketOut.bind((self.localhost, self.sOut))
        self.socketOut.connect((self.localhost, self.chanSocket))
        self.packetsSent = 0
        self.next = 0
        self.exitFlag = False
        
        
    def run(self):
        """
        Once the instance of a Sender is created run can be called to send the file
        Returns void
        """
        
        raw_packet = None
        readAmount = 512 #max number of bytes to be read into a file
        try:
            infile = open(self.sendFile, "rb")
        except IOError:
            infile.close()
            self.closePorts()
            sys.exit("File Not Found")        
        while self.exitFlag == False:
            data = infile.read(readAmount)
            if not data:
                data = "" 
                self.exitFlag = True
            sendPacket = Packet(0x497E,"dataPacket", self.next, len(data), data)
            self.packetsSent += 1 
            self.socketOut.send(sendPacket.encode())
            print("packet sent")
            acknowledged = False
            while not acknowledged: 
                self.socketIn.settimeout(1.0)
                try:
                    self.socketIn.listen(1)
                    if raw_packet == None:
                        raw_packet, addr = self.socketIn.accept()
                        raw_packet.settimeout(1)
                    packet = raw_packet.recv(self.bufferSize)
                    if packet == "": #No incoming packets from the Channel.
                        break
                    print("packet Received")
                    ackPacket = Packet.decode(packet)
                    if ackPacket.packetType != "0x497E" and ackPacket.packetType != 1 and ackPacket.seqno != self.next and ackPacket.checksum != ackPacket.getChecksum():        
                        sendPacket = Packet(0x497E,"dataPacket", self.next, len(data), data)
                        self.socketOut.send(sendPacket.encode())
                        print("packet resent- corrupted")
                        self.packetsSent += 1 
                        continue                            
                        
                    else:
                        acknowledged = True
                        self.next = 1 - self.next
                except socket.timeout:
                    print("packet resent - timed out")
                    sendPacket = Packet(0x497E,"dataPacket", self.next, len(data), data)
                    self.socketOut.send(sendPacket.encode())
                    self.packetsSent += 1 
        infile.close()
        print("Total packets sent including resends: {}".format(self.packetsSent))
    
    def checkRange(self, portnumber):
        """
        takes a Port number provided and checks to see if it is in the valid
        range.
        Returns a true if it is
        """
        if((portnumber > 1024) and (portnumber < 64000)):
            return True
        else:
            return False


    def closePorts(self):
        """
        Closes all open ports that have been created
        Returns void
        """
        self.socketIn.close()
        self.socketOut.close()
        sys.exit("All the open ports in Sender is now closed")
        
         
         
sender = Sender()
sender.run()
sender.closePorts()