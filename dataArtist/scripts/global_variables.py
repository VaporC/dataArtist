#===================
#DISPLAY
#===================
# access the current display with
d
# access all other displays with its number, like
d1, d2
# access the display data with 
d.l # l... layer

# access a specific layer using its index:
d.l0 # first layer
# or
d.l[0]
d.l1 # second layer 
# or
d.l[1]

# access all tools of a display:
d.tools['NAME OF THE TOOL']

#===================
#BUILTINS
#===================
# you can use all built-in functions of python, like
print dir, help, range

#===================
#EXTRA MODULES
#===================
# you can also access the following modules:
np # for numpy
QtGui, QtCore # from the Qt library

#===================
#SPECIAL FUNCTIONS
#===================
# to create a new display call
new(axes=3)
# or
new(axes=['x','y'])
# or
new(names=['LIST OF FILENAMES TO LOAD FROM'])
# or
new(data=np.ones(shape=(100,100), axes=3)) # to create on image layer
# or
new(data=np.ones(shape=(10,10), axes=2)) # to create 10 layers of 2d plots 

t = timed() #creates, registers and return a QtCore.QTimer instance
# or
timed(func_to_call, timeout=20)#executes func_to_call every 20 ms
# or
timed(func_to_call, timeout=20, stopAfter=10000)#... ends the execution after 10 sec
# or
timed(func_to_call, timeout=20, stopAfter=10000, stopFunc=done)#... execute 'done' when done
# or
timed(func_to_call, 20, 10000, done)#... same, but shorter