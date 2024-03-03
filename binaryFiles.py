class Binary:
    def convertToBinary(self,file):
        with open(file,'rb')as file:
            binary=file.read()
            return binary
    
    def convertToFile(binary,file):
        pass
