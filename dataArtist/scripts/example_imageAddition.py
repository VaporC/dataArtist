#add two images
#======================

# function to create random arrays
rand = np.random.normal

# create 2 random image-displays:
# ... values around 100
data1 = rand(size=(200, 200))+100
# ... values around -100
data2 = rand(size=(200, 200))-100

# two newe image displays:
n1 = new(data=[data1])
n2 = new(data=[data2])


# create a new display from the substracted n1, n2:
n3 = new(title='image sum', data=n1.l+n2.l, axes=3)

# or redure display n2 about 1000:
n2.l-=1000