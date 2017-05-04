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

        self.img_visual     = Image.new('RGB', (width, height), EGAPalette.WHITE)
        self.img_priority   = Image.new('RGB', (width, height), EGAPalette.RED)
        self.img_control    = Image.new('RGB', (width, height), EGAPalette.LIGHTGREY)
                  
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

        for command in self.draw_commands:
            self.process_command(command)                




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
            self.color = bytes[0]
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
    pictest = AGIPicture('picture.airbrush')     
    return 0

if __name__ == "__main__":
    sys.exit(run())
    
    
    














class NLAGIPicture():
    def __init__(self, filename=None, width=160, height=168):
        self.commands = []
        self.img_visual     = Image.new('RGB', (width, height), EGAPalette.WHITE)
        self.img_priority   = Image.new('RGB', (width, height), EGAPalette.RED)
        self.img_control    = Image.new('RGB', (width, height), EGAPalette.LIGHTGREY)
        self.width          = width
        self.height         = height
        self.is_rendered    = False

        self.scale_x        = 4
        self.scale_y        = 2

        self.ink_visual     = None
        self.ink_priority   = None
        self.ink_control    = None

        self.canvas_visual   = None
        self.canvas_priority = None
        self.canvas_control  = None

        self.px_visual      = None
        self.px_priority    = None
        self.px_control     = None

        self.brush_solid    = None
        self.brush_rect     = None
        self.brush_size     = None

        self.load(filename)

    def load(self, filename):
        draw_command = None
        with open(filename, "rb") as f:
            while True:
                  byte = f.read(1)
                  if byte:
                      if byte >= b'\xf0':
                          if draw_command is not None:
                              self.commands.append(draw_command)
                          draw_command = DrawCommand(byte)
                      else:
                          value = ord(byte)
                          draw_command.add_option(value)
                  else:
                      if draw_command is not None:
                          self.commands.append(draw_command)
                      break

    def process_commands(self):
        # set flag to show we have processed the draw commands already
        self.is_rendered = True
                  
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

        for command in self.commands:
            self.process_command(command)                


    def process_command(self, command):
        if command.get_command_type() == 'color':
            self.ink_visual = EGAPalette.COLORS[command.get_options()]
        elif command.get_command_type() == 'color off':
            self.ink_visual = None
        elif command.get_command_type() == 'priority':
            self.ink_priority = EGAPalette.COLORS[command.get_options()]
            if command.get_options() < 4:
                self.ink_control = self.ink_priority
            else:
                self.ink_control = None
        elif command.get_command_type() == 'priority off':
            self.ink_priority = None
            self.ink_control = None
        elif command.get_command_type() == 'fill':
            self.process_fill(command.get_options())
        elif command.get_command_type() == 'line':
            self.process_line(command.get_options())
        elif command.get_command_type() == 'y corner':
            self.process_corner(command.get_options(), type='y')
        elif command.get_command_type() == 'x corner':
            self.process_corner(command.get_options(), type='x')
        elif command.get_command_type() == 'short line':
            self.process_short_line(command.get_options())
        elif command.get_command_type() == 'pen':
            self.process_pen(command.get_options())
        elif command.get_command_type() == 'plot':
            self.process_plot(command.get_options())
                  
    def process_line(self, coord_list):
        x = -1
        y = -1
        for coords in coord_list:
            lx = x
            ly = y
            x = coords[0]
            y = coords[1]

            if self.ink_visual is not None:
                self.canvas_visual.line([(x, y), (x, y)], self.ink_visual)
                if (lx != -1 and ly != -1):
                    self.canvas_visual.line([(x, y), (lx, ly)], self.ink_visual)

            if self.ink_priority is not None:
                self.canvas_priority.line([(x, y), (x, y)], self.ink_priority)
                if (lx != -1 and ly != -1):
                    self.canvas_priority.line([(x, y), (lx, ly)], self.ink_priority)

            if self.ink_control is not None:
                self.canvas_control.line([(x, y), (x, y)], self.ink_control)
                if (lx != -1 and ly != -1):
                    self.canvas_control.line([(x, y), (lx, ly)], self.ink_control)
                  
    def process_corner(self, sequence, type='x'):
        alternate = 0
        if type == 'x':
            alternate = 1

        x = sequence[0]
        y = sequence[1]

        chain = sequence[2:]

        if self.ink_visual is not None:
            self.canvas_visual.line([(x, y), (x, y)], self.ink_visual)

        if self.ink_priority is not None:
            self.canvas_priority.line([(x, y), (x, y)], self.ink_priority)

        if self.ink_control is not None:
            self.canvas_control.line([(x, y), (x, y)], self.ink_control)

        for change in chain:
            lx = x
            ly = y
            if alternate == 0:
                y = change
            else:
                x = change
            alternate = 1 - alternate
            if self.ink_visual is not None:
                self.canvas_visual.line([(x, y), (lx, ly)], self.ink_visual)

            if self.ink_priority is not None:
                self.canvas_priority.line([(x, y), (lx, ly)], self.ink_priority)

            if self.ink_control is not None:
                self.canvas_control.line([(x, y), (lx, ly)], self.ink_control)
          
    def process_short_line(self, sequence):
        print(sequence)
        x = sequence[0]
        y = sequence[1]
        lx = x
        ly = y

        if self.ink_visual is not None:
            self.canvas_visual.line([(x, y), (x, y)], self.ink_visual)

        if self.ink_priority is not None:
            self.canvas_priority.line([(x, y), (x, y)], self.ink_priority)

        if self.ink_control is not None:
            self.canvas_control.line([(x, y), (x, y)], self.ink_control)

        for movement in sequence[2:]:
            nx = 1
            ny = 1
            
            lx = x
            ly = y

            breakdown = struct.unpack("B", chr(movement))
            bool(breakdown[0] & 128)

            
            xc = ((breakdown[0] & 112) >> 4) * (-1 if bool(breakdown[0] & 128) else 1)
            yc = (breakdown[0] & 7) * (-1 if bool(breakdown[0] & 8) else 1)

            x = x + xc
            y = y + yc

            if self.ink_visual is not None:
                self.canvas_visual.line([(x, y), (lx, ly)], self.ink_visual)

            if self.ink_priority is not None:
                self.canvas_priority.line([(x, y), (lx, ly)], self.ink_priority)

            if self.ink_control is not None:
                self.canvas_control.line([(x, y), (lx, ly)], self.ink_control)


    def draw_agi_line(self, canvas, fr_coords, to_coords):
        # canvas is the pixel array
        print '#placeholder#'
        

    def process_pen(self, brush_type):
        print brush_type        

        self.brush_solid    = bool(brush_type & 32)
        self.brush_rect     = bool(brush_type & 16)
        self.brush_size     = brush_type & 7

        print 'solid:' + str(self.brush_solid)
        print 'rect:' + str(self.brush_rect)
        print 'size:' + str(self.brush_size)

    def process_plot(self, coords):
        x = coords[0]
        print str(coords)

    def process_fill(self, coords):
        fill_list = []
        for fill_spot in coords:
            fill_list.append((fill_spot[0], fill_spot[1]))

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
                    
            elif self.ink_control is not None:
                if self.px_priority[px, py] == EGAPalette.LIGHTGREY:
                    add_neighbours = True
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


class NLDrawCommand():
    def __init__(self, command_byte):
        self._command_type = 'invalid'
        self._options = []
        
        if command_byte == b'\xf0':
            self._command_type = 'color'
        elif command_byte == b'\xf1':
            self._command_type = 'color off'
        elif command_byte == b'\xf2':
            self._command_type = "priority"
        elif command_byte == b'\xf3':
            self._command_type = "priority off"
        elif command_byte == b'\xf4':
            self._command_type = "y corner"
        elif command_byte == b'\xf5':
            self._command_type = "x corner"
        elif command_byte == b'\xf6':
            self._command_type = "line"
        elif command_byte == b'\xf7':
            self._command_type = "short line"
        elif command_byte == b'\xf8':
            self._command_type = "fill"
        elif command_byte == b'\xf9':
            self._command_type = "pen"   
        elif command_byte == b'\xfa':
            self._command_type = "plot"
        elif command_byte == b'\xff':
            self._command_type = "end"
        
    def get_command_type(self):
        return self._command_type
    
    def add_option(self, option):
        self._options.append(option)
        
    def get_options(self):
        if self._command_type == 'color':
            return self._options[0]
        elif self._command_type == 'color off':
            return ""
        elif self._command_type == 'priority':
            return self._options[0]
        elif self._command_type == 'priority off':
            return ""
        elif self._command_type == 'pen':
            return self._options[0]
        elif self._command_type == 'x corner':
            return self._options
        elif self._command_type == 'y corner':
            return self._options
        elif self._command_type == 'short line':
            return self._options
        elif self._command_type == 'plot':
            return self._options
        else:
            return self.get_coords()

    def get_coords(self):
        cnt = 0
        coords = []
        if self._command_type == 'short line':
            x = self._options[cnt]
            y = self._options[cnt]
            coords.append([x, y])

        else:
            while cnt < len(self._options):
                x = self._options[cnt]
                cnt = cnt + 1
                y = self._options[cnt]
                cnt = cnt + 1
                coords.append([x, y])
        return coords

    
