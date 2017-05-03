import sys
import struct
from PIL import Image, ImageDraw
from nl_palette import EGAPalette

def read_item(struct_type, stream):
    value = struct.unpack(struct_type,
        stream.read(struct.calcsize(struct_type)))
    if len(value) == 1:
        value = value[0]
    return value

def swap_byte_order(pair):
    return ((pair[1] << 8) + pair[0])

class AGIView():
    def __init__(self, filename=None):
        self.scale_x    = 2
        self.scale_y    = 2
        self.loops      = []

    def load(self, filename):
        stream = open(filename, "rb")

        loop_count = read_item("BBB", stream)[2]
        desc_ref = read_item("BB", stream)
        print swap_byte_order(desc_ref)
        loop_refs = []

        ## because of mirror loops, this can't be just a counted loop!




        cnt = 0
        pos = 5
        print '-----------------------'
        print 'loops: ' + str(loop_count)
        while cnt < loop_count:
            cnt = cnt + 1
            pos = pos + 2

            loop_ref = swap_byte_order(read_item("BB", stream))
            loop_refs.append(loop_ref)
            print 'Loop ' + str(cnt-1) + ' starting at ' + str(loop_ref)
            
            
        cnt = 0
        while cnt < loop_count:
            # loop_header
            loop_base = pos
            cnt = cnt + 1
            pos = pos + 1
            cel_count = read_item("B", stream)
            cel_refs = []
            
            print
            print 'Loop ' + str(cnt) + '(at ' + str(pos-1) + ')'
            print '-----------------------'
            print 'cels: ' + str(cel_count)

            c_cnt = 0
            while c_cnt < cel_count:
                c_cnt = c_cnt + 1
                pos = pos + 2
                # cel position (relative)

                cel_pos = swap_byte_order(read_item("BB", stream))
                cel_refs.append(cel_pos)
                print 'Cel ' + str(c_cnt) + ' starting at ' + str(cel_pos)

                print '::'+ str(pos)

            cel_width, cel_height = read_item("BB", stream)

            print 'CW::'
            print (cel_width, cel_height)

                

                

            if cnt > 1:
                break



            

        '''
            stream = open(filename)

            header = view_header(stream)


            def read_item(struct_type, stream):
    value = struct.unpack(struct_type,
        stream.read(struct.calcsize(struct_type)))
    if len(value) == 1:
        value = value[0]
    return value

def read_nts(stream, length=32):
    s = stream.read(length)
    return s.rstrip("\x00")


            read the number from the steam - read_item("L", stream)

            loop over number of loops, and add toa loop index table


            '''




class AGILoop():
    def __init__(self):
        self.cels = []

    def add_cel(self):
        newcel = AGICel()
        self.cels.append(newcel)

class AGICel():
    def __init__(self):
        self.img_cel = 1


def run():
    viewtest = AGIView()
    viewtest.load("view.simple")

    
        
    return 0

if __name__ == "__main__":
    sys.exit(run())
    
    
    
    
