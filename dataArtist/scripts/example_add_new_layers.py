# create a 2d array filled with 
# random values:
arr = np.random.normal(size=(200, 200))
# create a new display with that data:
n = new(axes=3)
n.l = arr
# at the moment our display has only 
# one data layer 
n.l1 = n.l0*3

for i in range(1,100): 
    d = np.random.normal(size=(200, 200))
    # with this command the created string 
    # will be executed at runtime
    exec('n.l%s = n.l%s+0.3*d' %(i, i-1))
