import math
import random
import numpy as np
import matplotlib.pyplot as plt
import time

def errorTest():
    class ErrorClass(Exception):
        pass

    raise ErrorClass("will this work?")

def test():
    def getYFromX(x: int):
        return math.floor((x + 1) * (x - 10)) # example equation

    def getXFromY(y: int, flipped=False) -> tuple:
        """
            How it works:
                FOILs out equation.
                Takes in the y and subtract y value from both sides to get 0=...
                Use Quadratic Formula
        """
        a = 1
        b = -1.9
        c = 10 - y

        if not flipped:
            x1 = math.floor((-b + math.sqrt(b ** 2 - 4 * a * c)) / (2 * a))
            x2 = math.floor((-b - math.sqrt(b ** 2 - 4 * a * c)) / (2 * a))
        
        else:
            a = -a
            b = -b
            c = -c - y

            x1 = math.floor((-b + math.sqrt(b ** 2 - 4 * a * c)) / (2 * a))
            x2 = math.floor((-b - math.sqrt(b ** 2 - 4 * a * c)) / (2 * a))

        return x1, x2

    for x in range(1,101):
        y = getYFromX(x)
    
    for y in range(1,101):
        x = getXFromY(y)

def setForest():
    data = {}
    # max y = 93.75
    # max x = -212.5

    def getYFromX(x: int):
        return math.floor((-0.00166204986 * x**2) + (-0.70637119 * x) + 18.6980609) # example equation

    def getXFromY(y: int, flipped=False) -> tuple:
        """
            How it works:
                FOILs out equation.
                Takes in the y and subtract y value from both sides to get 0=...
                Use Quadratic Formula
        """
        
        a = -0.00166204986 # these are all mathematically - on paper - figured out
        b = -0.70637119
        c = 18.6980609 - y

        if not flipped:
            x1 = math.floor((-b + math.sqrt(b ** 2 - 4 * a * c)) / (2 * a))
            x2 = math.floor((-b - math.sqrt(b ** 2 - 4 * a * c)) / (2 * a))
        
        else:
            a = -a
            b = -b
            c = -c - y

            x1 = math.floor((-b + math.sqrt(b ** 2 - 4 * a * c)) / (2 * a))
            x2 = math.floor((-b - math.sqrt(b ** 2 - 4 * a * c)) / (2 * a))

        return x1, x2

def mathTest():
    a = np.divide(100,3)
    b = 100/3

    c = np.divide(93.75, -56406.25)
    d = -0.00166204986

    print(c == d)

def pleaseWork():
    thokim_base_map = {}

    def setForest():
        # max y = 93.75
        # max x = -212.5
        
        prev_y = 0 # start at one x intercept where y = 0
        
        for x in range(-449, 26):
            y = math.floor(93.75/-56406.25 * (x + 450) * (x - 25))

            y_growth = y - prev_y

            halfway_point = (prev_y + y) // 2 # rounds down

            if y_growth > 0: # slope is positive
                for i in range(prev_y, halfway_point):
                    thokim_base_map[(x - 1, i)] = "forest"
                    print((x - 1, i))
                
                for i in range(halfway_point, y + 1):
                    thokim_base_map[(x, i)] = "forest"
                    print((x, i))
            
            elif y_growth < 0: # negative slope
                for i in range(halfway_point, prev_y):
                    thokim_base_map[(x - 1, i)] = "forest"
                
                for i in range(y, halfway_point):
                    thokim_base_map[(x, i)] = "forest"
            
            prev_y = y
    
    setForest()
    
    i = 0

    for coord in thokim_base_map:
        if i == 20:
            break
    
        else:
            plt.scatter(coord[0], coord[1])

            i += 1
    
    plt.show()

def pleaseWorkPt2():
    map = {(-5,25):"test"}
    
    prev_y = (-5) ** 2

    # for x in range(-4, 6):
    #     y = x**2

    #     plt.scatter(x, y)

    # plt.show()
    # return

    for x in range(-4, 6):
        y = x**2

        map[x, y] = "test"

        halfway = (prev_y + y) // 2

        change = y - prev_y

        if change > 0: # positive change
            # prev_y on bottom
            # y on top
            for i in range(prev_y, halfway):
                map[(x - 1, i)] = "test"
            
            for i in range(halfway, y):
                map[(x, i)] = "test"
    
        elif change < 0: # negative change
            # prev_y on top
            # y on bottom
            # left side = previous y
            for i in range(halfway, prev_y):
                map[(x - 1, i)] = "test"
            
            for i in range(y, halfway):
                map[(x, i)] = "test"
        
        prev_y = y
            
    for coord in map:
        plt.scatter(coord[0], coord[1])
        print(coord)
    
    plt.show()

thokim_base_map = {}

def umbrellaTestFunction():
    start = time.time()

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

    def setForest():
        thokim_base_map[(-450,-156)] = "forest"
        
        prev_y = -156
        
        # downwards opening
        for x in range(-449, 26):
            y = math.floor(93.75/-56406.25 * (x + 450) * (x - 25) - 156.25)

            setBetweenY("forest", x, prev_y, y)

            prev_y = y

            thokim_base_map[(x, y)] = "forest"
        
        prev_y = -156
        
        # upwards opening
        for x in range(-449, 26):
            # removed negative in first coefficient to flip to upwards opening
            y = math.floor(93.75/56406.25 * (x + 450) * (x - 25) - 156.25)

            setBetweenY("forest", x, prev_y, y)

            prev_y = y

            thokim_base_map[(x, y)] = "forest"
    
    setForest()

    # counter = 0

    # for coord in thokim_base_map:
    #     plt.scatter(coord[0], coord[1])
    #     print(coord)

    #     if counter == 30:
    #         break
    
    #     counter += 1
    
    # plt.show()

    end = time.time()

def bullshit():
    for x in range(-100,101):
        y = math.floor(93.75/56406.25 * (x + 450) * (x - 25) - 156.25)

        plt.scatter(x, y)
    
    plt.show()

def travelAcrossMapTest():
    spawnCoordX = random.randint(-500, 500)
    spawnCoordY = random.randint(-250, 250)

    spawnCoord = (spawnCoordX, spawnCoordY)

    plt.scatter(spawnCoord[0], spawnCoord[1])

    radius = 30

    current_cord = spawnCoord
    
    for i in range(60):
        while True:
            x = random.randint(current_cord[0] - radius, current_cord[0] + radius)
            y = random.randint(current_cord[1] - radius, current_cord[1] + radius)
        
            if abs(x - current_cord[0]) + abs(y - current_cord[1]) <= radius:
                plt.plot([current_cord[0], x], [current_cord[1], y])

                current_cord = (x, y)

                break

    plt.show()

if __name__ == '__main__':
    errorTest()