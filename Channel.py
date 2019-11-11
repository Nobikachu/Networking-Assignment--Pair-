import sys, socket, select, random
from Packet import Packet
class Channel:
    localHost = "127.0.0.1"
    def __init__(self):
        self.csin = int(sys.argv[1])
        self.csout = int(sys.argv[2])
        self.crin = int(sys.argv[3])
        self.crout = int(sys.argv[4])
        self.sin = int(sys.argv[5]) 
        self.rin = int(sys.argv[6])
        self.valueP = float(sys.argv[7])
        self.portNumbers = [self.csin, self.csout, self.crin, self.crout]
        self.magicno = "0x497e" 
        self.maxBuffSize = 1024 #The maximum size of the buffer
        self.validNumber()
        self.pRange()
        self.done = False
        self.halfDone = False
      
        self.socketcsin = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketcsout = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketcrin = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketcrout = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socketcsin.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.socketcsout.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.socketcrin.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.socketcrout.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)        
        self.socketcsin.bind((self.localHost, self.csin))
        self.socketcsout.bind((self.localHost, self.csout)) 
        self.socketcrin.bind((self.localHost, self.crin))
        self.socketcrout.bind((self.localHost, self.crout))

    def pRange(self):
        """Checks if the floating point/ souble precision is within the range
           0 <= P < 1
        """
        if self.valueP >= 1 or self.valueP < 0:
            print("P value should be in the range 0 or more and less than 1")
        
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
        
    def run(self):
        """Program go through infinite loop and wait for input on any one of 
           the of the two sockets (csout and crout) and set their default 
           receiver to the port numbers used by sender and receiver for the
           sockets sin and rin.
        """

        rlist = [self.socketcsin,self.socketcrin]
        sendConn = None
        recvConn = None        
        while True:
            read, write, error = select.select(rlist, [], [])                       
            for socket in read:
                if socket == self.socketcsin:                 
                    socket.listen(10)
                    sendConn, addr = socket.accept()
                    print("Packet received from sender")
                    rlist.append(sendConn)
                    packet = sendConn.recv(self.maxBuffSize)
                    self.socketcrout.connect((self.localHost, self.rin))
                    print("Packet processed and ready to send")
                    self.socketcrout.send(packet)
                    print("Packet Sent to receiver")
                elif socket == self.socketcrin:
                    socket.listen(10)
                    recvConn, addr = socket.accept() 
                    print("Packet received from receiver")
                    rlist.append(recvConn)
                    packet = recvConn.recv(self.maxBuffSize)
                    self.socketcsout.connect((self.localHost, self.sin))
                    print("Packet processed and ready to send")
                    self.socketcsout.send(packet)
                    print("Packet Sent to sender")
                elif socket == sendConn:
                    packet = sendConn.recv(self.maxBuffSize)
                    if packet == "": #No incoming packets
                        return 
                    decodedPacket = Packet.decode(packet)
                    print("Packet recieved from sender sc")
                    packet = self.introduceBitError(packet)
                    if packet is not None:                    
                        self.socketcrout.send(packet)
                        print("Packet Sent to receiver sc")

                elif socket == recvConn:
                    packet = recvConn.recv(self.maxBuffSize)
                    if packet == "": #No incoming packets
                        return         
                    decodedPacket = Packet.decode(packet)
                    print("Packet received from receiver rc")
                    packet = self.introduceBitError(packet)
                    if packet is not None:                    
                        self.socketcsout.send(packet)
                        print("Packet Sent to sender rc")

                                     
    
    def introduceBitError(self, packet):
        """
        Needs to be implemented here so the send structure works. SHould process the packet
        and then return the packet to go.
        """
        randomU = random.uniform(0,1) #Random variate u
        randomV = random.uniform(0,1) #Random variate v
        
        decodedPacket = Packet.decode(packet)
        if decodedPacket.magicno != self.magicno: #If the packet header does not equal '0x497E' then it should return back to the start of the loop.
            print("The magicno header " + str(decodedPacket.magicno) + " does not match '0x497E'!")
            return None
        if randomU < self.valueP: #Drops packet if u (uniformly distributed random variate) is smaller than P rate
            return None #Packets has been lost 
        else: #if the packet is not dropped
            if randomV < 0.1:
                randomInt = int(random.uniform(1,10)) #converts floating number to integer.
                decodedPacket.dataLen += randomInt #Increments dataLen field of the packet by a random integer between 1-10
                return decodedPacket.encode(False)            
            else:
                return packet
                
                
    def closePorts(self):
        """
        Closes all open ports that have been created
        Returns void
        """
        self.socketcsin.close()
        self.socketcsout.close()
        self.socketcrin.close()
        self.socketcrout.close()
        sys.exit("All the open ports in Channel is now closed.")
                
    
                
                
channel = Channel()
channel.run()
channel.closePorts()