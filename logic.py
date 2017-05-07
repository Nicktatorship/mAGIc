import sys
import struct
from agi_constants import *

class AGILogic(object):     
    def __init__(self, filename=None):
        self.stream = open(filename, "rb")
    
        position = 0
        bit_buffer = None

        while True:
            byte     = self.stream.read(1)
            position = position + 1
            if byte:
                print str(ord(byte)) + '\t' + hex(ord(byte))
            if position > 50:
                break

def run():
    logtest = AGILogic('logic.002')
    return 0

if __name__ == "__main__":
    sys.exit(run())
    
