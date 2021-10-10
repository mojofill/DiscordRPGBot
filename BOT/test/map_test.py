import matplotlib.pyplot as plt

realms = {
    "thokim":{},
    "retrollin":{},
    "ventus":{},
    "frilleon":{}
}

def getThokimMap():
    thokim_base_map = {}

    def setUpThokimBaseMap():
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

        thokim = realms["thokim"]
        thokim_town_origin = (333, 0)
        thokim[thokim_town_origin] = "thokim-town"

        # 333 block radius around the thokim_town_origin
        thokim_town_radius = 80

        thokim_town_points = getAllSquaresInRadius(
            x = thokim_town_origin[0],
            y = thokim_town_origin[1],
            radius = thokim_town_radius
        )

        for coord in thokim_town_points:
            thokim_base_map[coord] = "thokim-town"

    def setThokimDesert():
        x = -250

        def F(x: int):
            y = (34/6103.515625) * (x + 93.75) * (x + 250)

            return y

        while True:
            y = F(x)

            if y < 0:
                break
            
            thokim_base_map[(y, x)] = "desert"

            x += 1

        x = -500
        y = -83.125

        for x in range(-500, -49):
            y = (83.125 / 202500) * (x + 50) * (x + 950)

            x += 1
        
    def setMountains():
        m = - 187.5 / 550
        b = 218.75
        
        for x in range(-50, 501):
            y = m * x + b

            thokim_base_map[(x, y)] = "mountain"

    def setForest():
        # max y = 93.75
        # max x = -212.5
        
        for x in range(-450, 26):
            y = -93.75/56406.25 * (x + 450) * (x - 25)

            line_of_reflection = -156.25

            thokim_base_map[(x, line_of_reflection + y - 167.5)] = "forest"
            thokim_base_map[(x, line_of_reflection - y - 167.5)] = "forest"

    setThokimTown()
    setThokimDesert()
    setMountains()
    setForest()

    def checks():
        allCoords = list(thokim_base_map.keys())

        x = 1000

        list_of_x = []

        for coord in allCoords:
            if coord[0] not in list_of_x:
                list_of_x.append(coord[0])

                x -= 1
        
        if x > 0:
            class xIsNotContinous():
                pass
            
            raise xIsNotContinous
        
        print('all tests passed')

    checks()

    return thokim_base_map

realms["thokim"] = getThokimMap()