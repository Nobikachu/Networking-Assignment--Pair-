

import hashlib
class Packet:
    
    checksum = None
    
    def __init__(self,magicno,packetType, seqno, dataLen, data = None, checksum=None):
        try:
            self.magicno = hex(magicno)
        except:
            self.magicno = magicno
        if packetType == "dataPacket" or packetType == "0" or packetType == 0:
            self.packetType = 0 # using 0 for data packets and 1 for ack packets
        elif packetType == "acknowledgementPacket" or packetType == "1" or packetType == 1:
            self.packetType = 1
        else:
            raise TypeError
        self.seqno = seqno
        self.dataLen = int(dataLen)
        if data is None:
            self.data = b""
        else:
            self.data = data
        if checksum is not None:
            self.checksum = checksum
            
    def getChecksum(self):
        
        encoded_string = b""+str(self.magicno)+str(self.packetType)+str("{}".format(self.seqno))+str("{0:03}".format(self.dataLen))+self.data
        return hashlib.md5(encoded_string.encode('utf-8')).hexdigest()
    
    def encode(self, recalculateChecksum=True):
        """
        Encodes the packet data into a bit string for sending
        """
        
        magicno = str(int(str(self.magicno),0)) #Converting hex decimal to a integer. Then convert it into a string.
        encoded_string = b""+str(self.magicno)+str(self.packetType)+str(self.seqno)+str("{0:03}".format(self.dataLen))+self.data #"," used to separate the data length and the data.
        if recalculateChecksum:
            checksum = hashlib.md5(encoded_string.encode('utf-8')).hexdigest()
        else:
            checksum = self.checksum
        encoded_string = encoded_string + checksum
        return encoded_string
        
    @staticmethod    
    def decode(encoded_string):
        """
        Takes an encoded string and decodes it back to the original.
        Checks checksum and ensures packet is recieved as expected
        """
        checksum = encoded_string[-32:] #selects the last 32 chars of the string which is the hash
        dataLength = encoded_string[8:11]
        if encoded_string[6] == '0':
            packetType = "dataPacket" 
        elif encoded_string[6] == '1':
            packetType = "acknowledgementPacket"
        else:
            packetType = "dataPacket"
        if dataLength == 0: 
            data = None
        else:
            data = encoded_string[12:-32]
        return Packet(encoded_string[:6], packetType, encoded_string[7], dataLength, data, checksum)#magicno,packetType,seqno,datalen,data,checksum

        
    def __str__(self):
        return("MagicNo: {}\nType: {}\nSequence Number: {}\nData Length: {}".format(self.magicno,self.packetType,self.seqno,self.dataLen))

