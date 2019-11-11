import sys, socket, select
from Packet import Packet

class Receiver:
    localHost = "127.0.0.1"
    def __init__(self):
        self.rin = int(sys.argv[1])
        self.rout = int(sys.argv[2])
        self.crin = int(sys.argv[3])
        self.fileName = sys.argv[4]
        self.portNumbers = [self.rin, self.rout]
        self.validNumber() 
        
        self.expected = 0 #Local integer
        self.bufferSize = 1024
        self.magicno = '0x497e'
        
        self.files = []
        
        localHost = socket.gethostbyname(socket.gethostname())
        self.socketrin = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketrout = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketrin.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.socketrout.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.socketrin.bind((self.localHost, self.rin))
        self.socketrout.bind((self.localHost, self.rout))
        
        self.socketrout.settimeout(10)
        '''
        try:
            self.socketrout.connect((localHost, self.crin))
        except:
            sys.exit("Socket error (Transport endpoint is not connected)")
        '''
        
    def validNumber(self):
        """Checks if the port numbers are within the range 1024 and 64000.
           Also checks if the number is integer and all the port numbers are unique.
        """
        nums = []
        for pnum in self.portNumbers:
            if pnum > 64000 or pnum < 1024:
                sys.exit("Port number must be between 1024 and 64000")
            if pnum in nums: #Checks if the port numbers are unique.
                sys.exit("Port number must be unique!") 
            nums.append(pnum)
        #Change the type to integer since the port number should be a integer. 
        
    def run(self):
        """Once the instance of a Receiever is created. "run" can be called to
           to receive and store the file
           """
        raw_packet = None
        try:
            outfile = open(self.fileName, "w") #Receiver opens a file with supplied filename for writing
        except IOError:
            sys.exit("File Not Found")        
        for file in self.files: #Checks if the file already exists. 
            if file == self.fileName:
                sys.exit("File already exists")
        self.files.append(self.fileName)
        expected = 0
        while True:
            self.socketrin.listen(5)
            if raw_packet == None:
                raw_packet, addr = self.socketrin.accept()
                self.socketrout.connect((self.localHost, self.crin))
            packet = raw_packet.recv(self.bufferSize)
            if packet == "": #No more incoming packets from Channel.
                return         
            print("Packet received")   
            decodedPacket = Packet.decode(packet)
            if decodedPacket.seqno != expected and decodedPacket.packetType != 0 and decodedPacket.checksum != decodedPacket.getChecksum() and decodedPacket.magicno != self.magicno:
                newPacket = Packet(0x497E, "acknowledgementPacket", int(decodedPacket.seqno), 0, decodedPacket.data)
                self.socketrout.send(newPacket.encode())
                print("Sent Packet, Packet corrupted")
            else:
                newPacket = Packet(0x497E, "acknowledgementPacket", int(decodedPacket.seqno), 0) #Datafield is empty.
                self.socketrout.send(newPacket.encode())
                print("Sent Packet Packet all good")
                expected = 1 - expected
                if decodedPacket.dataLen != 0:
                    outfile.write(decodedPacket.data)
                else:
                    outfile.close()  
                    self.closePorts()
            
        

    def closePorts(self):
        """
        Closes all open ports that have been created
        Returns void
        """
        self.socketrin.close()
        self.socketrout.close()
        sys.exit("All the open ports in Receiver is now closed")
            
        
    
                
                
receiver = Receiver()
receiver.run()
receiver.closePorts()