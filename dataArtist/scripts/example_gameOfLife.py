#This example shows the Conways GAME OF LIFE  
#==========================================

#This example needs an image display!

#Because all values are either one or zero
# we can speed up the display process
# with fixing the histogram range between 0-1:
cbar = d.tools['Colorbar']
cbar.param('autoLevels').setValue(False)
cbar.param('autoHistogramRange').setValue(False)
cbar.setLevels(0,0.1)


# let's define some variables:
sizeX = 50
sizeY = 50


#random 2d-array filled with values between 0 and 10:
data = np.random.randint(10, size=(sizeX, sizeY))
# all values bigger 1 become 1
# the abount of px == 1 if now 20%
data[data>1] = 0
#new display filled with that data


#the actual gameOfLife function
def processNeighbours(x, y, array):
    nCount = 0
    for j in range(y-1,y+2):
        for i in range(x-1,x+2):
            if not(i == x and j == y):
                if array[i][j] != -1:
                    nCount += array[i][j]
    if array[x][y] == 1 and nCount < 2:
        return 0
    if array[x][y] == 1 and nCount > 3:
        return 0
    if array[x][y] == 0 and nCount == 3:
        return 1
    else:
        return array[x][y]



def update():
    global sizeX, sizeY, processNeighbours, d, data
    for i in range(1,sizeX-1):
        for j in range(1,sizeY-1):
            data[i][j] = processNeighbours(i, j, data)
    d.l = data

timed(update, 50)