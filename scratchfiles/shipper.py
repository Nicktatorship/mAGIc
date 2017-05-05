import sys
from math import *

class shipper(object):
    def __init__(self, x=0, y=0, sp=5, head=90):
        self.coords = (x, y)
        self.speed = sp
        self.heading = head
        
    def update(self):
        new_x, new_y = self.coords
        if self.speed > 0:
            new_x = self.coords[0] + int(self.speed * sin(radians(self.heading)))
            new_y = self.coords[1] + int(self.speed * cos(radians(self.heading)))
            self.coords = (new_x, new_y)

    def report(self):
        report_buffer = 'C: ' + str(self.coords)
        report_buffer = report_buffer + '\tH: ' + str(self.heading)
        report_buffer = report_buffer + '\tS: ' + str(self.speed)
        return report_buffer

def run():
    ships = []
    turns = 9
    ships.append(shipper(-17,3,5,90))
    ships.append(shipper(3,-5,2,0))
        
    for i in range(turns):
        j = 0
        for ship in ships:
            j = j + 1
            ship.update()
            print 'Ship ' + str(j) + '\t' + ship.report()

        check_collisions(list(ships))


    return 0

def check_collisions(shiplist=[]):
    if len(shiplist) != 0:
        testships = shiplist
        for shippie in shiplist:
            testships.remove(shippie)
            for testship in testships:
                if testship.coords == shippie.coords:
                    print '** COLLIDE'
        
    


if __name__ == "__main__":
    sys.exit(run())
