import sys
import struct
from PIL import Image, ImageDraw
from palettes import EGAPalette
from agi_constants import *


def get_coordinates(coords):
    x = ord(coords[0])
    y = ord(coords[1])
    return x, y

class AGIPicture(object):
        
    def __init__(self, filename=None, width=160, height=168):
        self.width          = width
        self.height         = height
        self.is_rendered    = False

        self.scale_x        = 4
        self.scale_y        = 2
        
        self.draw_commands = []
        self.stream = open(filename, "rb")
        self.load()
    
    def load(self):
        position = 0
        bit_buffer = None

        while True:
            byte     = self.stream.read(1)
            position = position + 1
            if byte:                
                if byte >= IS_COMMAND:
                    if bit_buffer is not None:
                        self.add_picture_command(bit_buffer)
                    bit_buffer = byte
                else:
                    bit_buffer = bit_buffer + byte
            else:
                if bit_buffer is not None:
                    self.add_picture_command(bit_buffer)       
                break

    def add_picture_command(self, stream):
        com = AGIPictureCommand(stream)
        self.draw_commands.append(com)

    def process_commands(self):
        # set flag to show we have processed the draw commands already
        self.is_rendered = True

        self.img_visual     = Image.new('RGB', (self.width, self.height), EGAPalette.WHITE)
        self.img_priority   = Image.new('RGB', (self.width, self.height), EGAPalette.RED)
        self.img_control    = Image.new('RGB', (self.width, self.height), EGAPalette.LIGHTGREY)
                  
        # set up pixel access
        self.px_visual = self.img_visual.load()
        self.px_priority = self.img_priority.load()
        self.px_control = self.img_control.load()

        # set up draw access
        self.canvas_visual   = ImageDraw.Draw(self.img_visual)
        self.canvas_priority = ImageDraw.Draw(self.img_priority)
        self.canvas_control  = ImageDraw.Draw(self.img_control)

        # set up layer draw colours
        self.ink_visual     = None
        self.ink_priority   = None
        self.ink_control    = None

        limit = -1
        cnt = 0

        for draw_command in self.draw_commands:
            cnt = cnt + 1
            self.process_command(draw_command)
            if cnt == limit:
                break

    def process_command(self, com):
        if com.command_type == COLOR:
            self.ink_visual = EGAPalette.COLORS[com.color]
        elif com.command_type == COLOR_OFF:
            self.ink_visual = None
        elif com.command_type == PRIORITY:
            self.ink_priority = EGAPalette.COLORS[com.color]
            self.ink_control = (self.ink_priority if com.color < 4 else None)            
        elif com.command_type == PRIORITY_OFF:
            self.ink_priority = None
            self.ink_control = None
        elif com.command_type == FILL:
            self.process_fill(com.coordinates)
        elif com.command_type == LINE or com.command_type == SHORT_LINE or \
             com.command_type == X_CORNER or com.command_type == Y_CORNER:
            self.process_draw(com.coordinates)
        elif com.command_type == PEN:
            self.pen_solid  = com.brush_solid
            self.pen_rect   = com.brush_rect
            self.pen_size   = com.brush_size
        elif com.command_type == PLOT:
            self.process_plot(com.coordinates)

    def process_draw(self, coordinates=[]):           
        for line_coords in coordinates:
            
            if self.ink_visual is not None:
                self.canvas_visual.line(line_coords, self.ink_visual)

            if self.ink_priority is not None:
                self.canvas_priority.line(line_coords, self.ink_priority)

            if self.ink_control is not None:
                self.canvas_control.line(line_coords, self.ink_control)

    def process_fill(self, coordinates):
        fill_list = []
        for fill_coords in coordinates:
            fill_list.append(fill_coords)

        for pixel in fill_list:
            add_neighbours = False
            px = pixel[0]
            py = pixel[1]

            if self.ink_visual is not None:
                if self.px_visual[px, py] == EGAPalette.WHITE:
                    add_neighbours = True
                    self.px_visual[px, py] = self.ink_visual

                    if self.ink_priority is not None:
                        self.px_priority[px, py] = self.ink_priority

                    if self.ink_control is not None:
                        self.px_control[px, py] = self.ink_control

            elif self.ink_priority is not None:
                if self.px_priority[px, py] == EGAPalette.RED:
                    add_neighbours = True
                    self.px_priority[px, py] = self.ink_priority

                if self.ink_control is not None:
                    self.px_control[px, py] = self.ink_control

            if add_neighbours:
                if px > 0:
                    fill_list.append((px-1, py))
                if px < self.width-1:
                    fill_list.append((px+1, py))
                if py > 0:
                    fill_list.append((px, py-1))
                if py < self.height-1:
                    fill_list.append((px, py+1))

    def process_plot(self, coordinates=[]):
        print '!'
                     
    def get_image(self, type='visual'):
        if not self.is_rendered:
            self.process_commands()
                  
        if type == 'control':
            return self.img_control
        elif type == 'priority':
            return self.img_priority
        else:
            return self.img_visual

    def get_upscaled(self, type='visual'):
        return self.get_image(type).resize((self.width * self.scale_x, self.height * self.scale_y))

    def save_image(self, type='visual'):
        output = self.get_upscaled(type)
        filename = 'nl' + type + '_test.png'
        output.save(filename)




class AGIPictureCommand(object):
    def __init__(self, bytes):
        self.command_type = COMMAND_DEFS[ord(bytes[0])]

        self.color = None
        self.coordinates = []
        self.load(bytes[1:])

        self.brush_solid = None
        self.brush_rect = None
        self.brush_size = None
        
    def load(self, bytes):
        if self.command_type == COLOR or self.command_type == PRIORITY:
            self.color = ord(bytes[0])
        elif self.command_type == Y_CORNER or self.command_type == X_CORNER:
            self.load_command_corner(bytes)
        elif self.command_type == LINE:
            self.load_command_line(bytes)
        elif self.command_type == SHORT_LINE:
            self.load_command_short(bytes)
        elif self.command_type == FILL:
            self.load_command_fill(bytes)
        elif self.command_type == PEN:
            self.load_command_pen(bytes)
        elif self.command_type == PLOT:
            self.load_command_plot(bytes)

    def load_command_corner(self, bytes):
        alternate = (False if self.command_type == Y_CORNER else True)
        x, y = get_coordinates(bytes[0:2])
        self.coordinates.append((x, y, x, y))

        for new_coordinate in bytes[2:]:
            lx, ly = (x, y)
            if alternate:
                x = ord(new_coordinate)
            else:
                y = ord(new_coordinate)
            alternate = not alternate
            self.coordinates.append((lx, ly, x, y))

    def load_command_line(self, bytes):
        x, y = get_coordinates(bytes[0:2])
        self.coordinates.append((x, y, x, y))

        bytes = bytes[2:]
        while len(bytes) > 1:
            lx, ly = (x, y)
            x, y = get_coordinates(bytes[0:2])
            self.coordinates.append((lx, ly, x, y))
            bytes = bytes[2:]
        
    def load_command_short(self, bytes):
        x, y = get_coordinates(bytes[0:2])
        self.coordinates.append((x, y, x, y))

        for movement in bytes[2:]:
            lx, ly = (x, y)

            breakdown = ord(movement)
            
            x = x + ((breakdown & 112) >> 4) * (-1 if bool(breakdown & 128) else 1)
            y = y + (breakdown & 7) * (-1 if bool(breakdown & 8) else 1)

            self.coordinates.append((lx, ly, x, y))

        
    def load_command_fill(self, bytes):
        while len(bytes) > 1:
            self.coordinates.append((get_coordinates(bytes[0:2])))
            bytes = bytes[2:]
        
    def load_command_pen(self, bytes):
        brush_type = ord(bytes[0])
        self.brush_solid = bool(brush_type & 32)
        self.brush_rect = bool(brush_type & 16)
        self.brush_size = brush_type & 7
        
    def load_command_plot(self, bytes):
        while len(bytes) > 1:
            self.coordinates.append((get_coordinates(bytes[0:2])))
            bytes = bytes[2:]

                
def run():
    pictest = AGIPicture('picture.003')
    pictest.process_commands()
    pictest.get_upscaled('visual').save('testnewvis.png', format="PNG")
    return 0

if __name__ == "__main__":
    sys.exit(run())
    
