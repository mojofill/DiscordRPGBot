import math
import numpy as np

realms = {
    "thokim":None,
    "retrollin":None,
    "ventus":None,
    "frilleon":None
}

def getThokimMap():
    thokim_base_map = {}

    def setUpThokimBaseMap():
        """Sets in ALL the coordinates in the Thokim base map"""
        map_x_width = 1000
        map_y_length = 500

        x = 0
        y = 0

        iter_x = x
        iter_y = y

        for i in range(4):
            for iter_x_add in range(map_x_width // 2):
                for iter_y_add in range(map_y_length // 2):
                    iter_x = x
                    iter_y = y
                    
                    if i == 0:
                        iter_x += iter_x_add
                        iter_y += iter_y_add
                    
                    elif i == 1:
                        iter_x -= iter_x_add
                        iter_y += iter_y_add
                    
                    elif i == 2:
                        iter_x += iter_x_add
                        iter_y -= iter_y_add

                    else:
                        iter_x -= iter_x_add
                        iter_y -= iter_y_add

                    thokim_base_map[(iter_x, iter_y)] = "grass"
    
    def setBetweenY(border_type: str, x: int, prev_y: int, y: int):
        y_growth = y - prev_y

        halfway_point = (prev_y + y) // 2 # rounds down

        if y_growth > 0: # slope is positive
            for i in range(prev_y, halfway_point):
                thokim_base_map[(x - 1, i)] = border_type
            
            for i in range(halfway_point, y + 1):
                thokim_base_map[(x, i)] = border_type
        
        elif y_growth < 0: # negative slope
            for i in range(halfway_point, prev_y):
                thokim_base_map[(x - 1, i)] = border_type
            
            for i in range(y, halfway_point):
                thokim_base_map[(x, i)] = border_type
        
        prev_y = y
                
    def setMapBorders():
        for y in [-250, 250]:
            for x in range(-500, 501):
                thokim_base_map[x, y] = 'b|map-border'
            
        
        for x in [-500, 500]:
            for y in range(-250, 251):
                thokim_base_map[x, y] = 'b|map-border'

    setMapBorders()  
    # setUpThokimBaseMap()

    def setThokimTown():
        def getAllSquaresInRadius(x: int, y: int, radius: int) -> list:
            points = [(x, y)]

            iter_x = x
            iter_y = y

            for i in range(4):
                for iter_y_add in range(radius - 1):
                    for iter_x_add in range(radius - 1):
                        iter_x = x
                        iter_y = y
                        
                        if i == 1:
                            iter_x -= iter_x_add
                            iter_y -= iter_y_add
                        
                        elif i == 2:
                            iter_x += iter_x_add
                            iter_y -= iter_y_add
                        
                        elif i == 3:
                            iter_x -= iter_x_add
                            iter_y += iter_y_add
                        
                        else:
                            iter_x += iter_x_add
                            iter_y += iter_y_add

                        if (abs(iter_x - x) + abs(iter_y - y)) <= radius:
                            points.append((iter_x, iter_y))
            
            return points

        thokim_town_origin = (333, 0)
        thokim_base_map[thokim_town_origin] = "b|thokim-town"

        # 333 block radius around the thokim_town_origin
        thokim_town_radius = 80

        thokim_town_points = getAllSquaresInRadius(
            x = thokim_town_origin[0],
            y = thokim_town_origin[1],
            radius = thokim_town_radius
        )

        for coord in thokim_town_points:
            thokim_base_map[coord] = "b|thokim-town"

    def setThokimDesert():
        x = -250

        def F(x: int):
            y = math.floor((34/6103.515625) * (x + 93.75) * (x + 250))

            return y

        prev_y = 0

        while True:
            y = F(x)

            if y < 0:
                break

            setBetweenY("b|desert", x, prev_y, y)
            
            thokim_base_map[(y, x)] = "b|desert"

            x += 1

            prev_y = y

        prev_y = 0

        for x in range(-499, -49):
            y = math.floor((83.125 / 202500) * (x + 50) * (x + 950))

            setBetweenY("b|desert", x, prev_y, y)
        
            thokim_base_map[(x, y)] = "b|desert"

            prev_y = y
        
        # set the wall borders of the desert

        for y in range(-93, 251):
            thokim_base_map[(-500, y)] = "b|desert"
        
        for x in range(-500, -449):
            thokim_base_map[(x, 250)] = "b|desert"
        
    def setMountains():
        m = - 187.5 / 550
        b = 218.75
        
        for x in range(-50, 501):
            y = m * x + b

            thokim_base_map[(x, y)] = "b|mountain"
        
        for x in range(-449, 501):
            thokim_base_map[(x, 250)] = "b|mountain"
        
        for y in range(42, 251):
            thokim_base_map[(250, y)] = "b|mountain"

    def setForest():
        thokim_base_map[(-450,-156)] = "b|forest"
        
        prev_y = -156
        
        # downwards opening
        for x in range(-449, 26):
            y = math.floor(93.75/-56406.25 * (x + 450) * (x - 25) - 156.25)

            setBetweenY("b|forest", x, prev_y, y)

            prev_y = y

            thokim_base_map[(x, y)] = "b|forest"
        
        prev_y = -156
        
        # upwards opening
        for x in range(-449, 26):
            # removed negative in first coefficient to flip to upwards opening
            y = math.floor(93.75/56406.25 * (x + 450) * (x - 25) - 156.25)

            setBetweenY("b|forest", x, prev_y, y)

            prev_y = y

            thokim_base_map[(x, y)] = "b|forest"

    setThokimTown()
    setThokimDesert()
    setMountains()
    setForest()

    return thokim_base_map

def getRetrollinMap():
    pass

class _Map:
    def __init__(self) -> None:
        self.Thokim = getThokimMap()

Map = _Map()