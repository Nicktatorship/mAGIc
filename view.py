import sys
import struct
from PIL import Image, ImageDraw
from palettes import EGAPalette


def read_item(struct_type, stream):
    value = struct.unpack(struct_type,
        stream.read(struct.calcsize(struct_type)))
    if len(value) == 1:
        value = value[0]
    return value

def swap_byte_order(pair):
    return ((ord(pair[1]) << 8) + ord(pair[0]))

class AGIView():
    def __init__(self, filename=None):
        self.scale_x     = 4
        self.scale_y     = 2
        self.loops       = []
        self.stream      = open(filename, "rb")
        self.description = None
        self.load()

    def load(self):
        position    = 0
        bit_buffer  = None

        while True:
            byte     = self.stream.read(1)
            position = position + 1
            if byte:
                if bit_buffer is not None:
                    bit_buffer = bit_buffer + byte
                else:
                    bit_buffer = byte
            else:
                break
            
        loop_count = ord(bit_buffer[2])
        desc_ref = swap_byte_order(list(bit_buffer[3:5]))
        if desc_ref != 0:
            self.description = bit_buffer[desc_ref:]

        loop_positions = []
        for i in range(loop_count):
            spot = 5 + i*2
            loopref = swap_byte_order(list(bit_buffer[spot:spot+2]))
            loop_positions.append(loopref)

        endpoint = len(bit_buffer) - 1
        for offset in loop_positions:
            loop_buffer = bit_buffer[offset:]
            build_loop = AGIViewLoop(loop_buffer)
            self.loops.append(build_loop)

    def get_all_frames(self, upscaled=False):
        looplist = []
        for loop in self.loops:
            looplist.append(loop.get_frames(upscaled))
        return looplist

class AGIViewLoop():
    def __init__(self, loop_data):

        
        self.cels = []
        cel_count = ord(loop_data[0])
        cel_positions = []
        for i in range(cel_count):
            spot = 1 + i*2
            celref = swap_byte_order(list(loop_data[spot:spot+2]))
            cel_positions.append(celref)

        endpoint = len(loop_data) -1
        for offset in cel_positions:
            cel_buffer = loop_data[offset:]
            build_cel = AGIViewCel(cel_buffer)
            self.cels.append(build_cel)

    def get_frames(self, upscaled=False):
        cel_list = []
        for cel in self.cels:
            cel_list.append(cel.get_frame(upscaled))

        return cel_list

class AGIViewCel():
    def __init__(self, cel_data):
        self.is_rendered    = False
        self.scale_x        = 4
        self.scale_y        = 2

        self.width = ord(cel_data[0])
        self.height = ord(cel_data[1])
        self.transp = ord(cel_data[2]) & 15
        self.mirror = (ord(cel_data[2]) & 128) >> 4

        self.cel_sheet  = Image.new('RGB', (self.width, self.height), EGAPalette.COLORS[self.transp])
        self.cel_pixels = self.cel_sheet.load()
        self.cel_draw   = ImageDraw.Draw(self.cel_sheet)

        cnt = 0
        x   = 0
        y   = 0
        for instruction in cel_data[3:]:
            cnt = cnt + 1
            pixel_color = (ord(instruction) & 240) >> 4
            pixel_ink = EGAPalette.COLORS[pixel_color]
            pixel_run   = ord(instruction) & 15

            if pixel_run != 0 and pixel_run != 0:
                self.cel_draw.line((x, y, x + pixel_run, y), pixel_ink)
                x = x + pixel_run
            else:
                y = y + 1
                x = 0
                if y > self.height:
                    break
                
        self.is_rendered = True

    def get_frame(self, upscaled=False):
        if upscaled:
            return self.get_upscaled()
        else:
            return self.cel_sheet
                
    def get_upscaled(self):
        return self.cel_sheet.resize((self.width * self.scale_x, self.height * self.scale_y))

    def save_image(self):
        output = self.get_upscaled()
        filename = 'view_test.png'
        output.save(filename)

def run():
    #viewtest = AGIView("view.simple")
    
    viewtest = AGIView("view.220")
    viewtest = AGIView("view.000")

    fullsheet = viewtest.get_all_frames(true)
    fullsheet[3][3].save('testfile.png')

    

    
        
    return 0

if __name__ == "__main__":
    sys.exit(run())
    
    
    
    

