#create a new display with 3 dimensions:
n = new(axes=['x', 'y','i'])

nx = 0
ny = 0
def update():
    # make nx, ny known to the function:
    global nx, ny
    # create a 2d array from a function
    # and assign it to the new display
    n.l = np.fromfunction(lambda x,y: 
        np.sin(x*nx)+np.cos(y*ny), (100,100))
    # increase counter value
    nx += 0.001
    ny += 0.003
# create a timer to coll 'update' every 20 ms:
timed(update, 20, 20000)