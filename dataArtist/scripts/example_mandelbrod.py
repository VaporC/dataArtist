# this example animates a mandelbrot for us! yeah.
# this is the basic function for it:
def mandelbrot(LowX, HighX, LowY, HighY, stepx, stepy, maxiter):
    "creates a numeric array of the mandelbrot function"
    #if maxiter > 11: maxiter = 11  #for your own protection
    xx = np.arange(LowX, HighX, (HighX-LowX)/stepx)
    yy = np.arange(HighY, LowY, (LowY-HighY)/stepy) * 1.0j
    #somtimes these arrays are too big by one element???
    xx = xx[:stepx]
    yy = yy[:stepy]
    c = np.ravel(xx+yy[:,np.newaxis])
    z = np.zeros(c.shape, np.complex)
    output = np.zeros(c.shape) + 1
    for iter in range(maxiter):
        np.multiply(z, z, z)
        np.add(z, c, z)
        np.add(output, np.greater(abs(z), 2.0), output)
    output.shape = (stepy, stepx)
    return np.transpose(output)

# let's define some variables:
l_val, r_val = -2.12, 0.1247627
t_val, b_val = -1.223, 0.01124
l_inc, r_inc = .03, -.02
t_inc, b_inc = .03, -.005
res = (200,200) # image resolution
iterations = 11 # image depth - shouldn't be to high 

# we want to have the output on a new display:
n = new(axes=3)
# make it fullscreen:
n.setFullscreen()
n.hideTitleBar()
def update():
    #updates mandelbrod via varying variables
    global l_val, l_inc, r_val, r_inc, t_val, t_inc,b_val,b_inc, mandelbrot, res, iterations
    n.l = mandelbrot(l_val, r_val, t_val, b_val, res[0], res[1], iterations)
    l_val += l_inc
    r_val += r_inc
    t_val += t_inc
    b_val += b_inc

def done():
    n.setFullscreen()
    n.showTitleBar()


# create a timer to coll 'update' every 20 ms:
timed(update, 20, 10000, done)
