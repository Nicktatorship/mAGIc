import sys
from sdl2 import *
import sdl2.ext
import cStringIO

from PIL import Image, ImageDraw
from palettes import EGAPalette
from picture import AGIPicture
from view import AGIView

class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, EGAPalette.BLACK)
        super(SoftwareRenderer, self).render(components)

TARGET_DIMENSIONS = (320, 336)
RENDER_DIMENSIONS = (1280, 672)
TARGET_DIMENSIONS = (160, 200)
RENDER_DIMENSIONS = (640, 400)

def run():
    sdl2.ext.init()
    window = sdl2.ext.Window("Game Test", size=RENDER_DIMENSIONS)
    world = sdl2.ext.World()
    spriterenderer = SoftwareRenderer(window)
    world.add_system(spriterenderer)
    
    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    imgdata = cStringIO.StringIO()
    imgdat2 = cStringIO.StringIO()

    import_pic = AGIPicture("picture.003")
    import_pic.get_upscaled('visual').save("checker.png")
    import_pic.get_upscaled('visual').save(imgdata, format="PNG")

    import_view = AGIView("view.000")
    import_view.get_all_frames(True)[1][1].save(imgdat2, format="PNG")

    surfy = sdl2.ext.load_image(imgdata, enforce="PIL")
    background = factory.from_surface(surfy)
    background.position = 0, 16
    spriterenderer.render(background)

    surface2 = sdl2.ext.load_image(imgdat2, enforce="PIL")
    player = factory.from_surface(surface2)
    player.position = 80, 30
    spriterenderer.render(player)

    window.show()
    window.refresh()

    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        
    return 0


if __name__ == "__main__":
    sys.exit(run())
    
