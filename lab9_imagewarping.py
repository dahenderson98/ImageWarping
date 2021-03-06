# -*- coding: utf-8 -*-
"""Lab9-ImageWarping.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vu4XFCJI6QWVVNSmg8WXt6Qiv_oyw_OB

# Image Warping Lab

## Part 1: Interpolation

Since we are going to be warping images, we need to make sure we have a good interpolation function to deal with inexact pixel locations.

In the cell below, we want to scale an image by a factor of 2.30 in both x and y. **Write a function called "interpolate" that performs bilinear interpolation.** This function should take in the image and a location (x,y) of interest. It then uses the nearby pixels to that location to interpolate and return an RGB value.
"""

from os import sendfile
import matplotlib.pyplot as plt
import numpy as np
import math

#Your bilinear interpolation function
#x and y may be inexact locations
def interpolate(image, target_y, target_x):
    x_left = math.floor(target_x)
    x_right = math.ceil(target_x)
    y_bottom = math.floor(target_y)
    y_top = math.ceil(target_y)
    # print("targetX: " + str(target_x))
    # print("targetY: " + str(target_y))
    # print("LeftX: " + str(x_left))
    # print("RightX: " + str(x_right))
    # print("BottomY: " + str(y_bottom))
    # print("TopY: " + str(y_top) + '\n')

    imgh, imgw, _ = image.shape
    if x_right > imgw-1 or x_left < 0 or y_top > imgh-1 or y_bottom < 0:
      target_shade = [0,0,0]
    elif y_bottom == y_top:
      target_shade = (1-(target_x - x_left)) * image[y_top,x_left,:] + (1-(x_right - target_x)) * image[y_top,x_right,:]
    else: 
      mid_x_top_shade = (1-(target_x - x_left)) * image[y_top,x_left,:] + (1-(x_right - target_x)) * image[y_top,x_right,:]
      mid_x_bottom_shade = (1-(target_x - x_left)) * image[y_bottom,x_left,:] + (1-(x_right - target_x)) * image[y_bottom,x_right,:]
      target_shade = (1-(y_top - target_y)) * mid_x_top_shade + (1-(target_y - y_bottom)) * mid_x_bottom_shade
    
    # print(target_shade)
    return np.multiply(target_shade, 255)



filename = "test.png"
im = plt.imread(filename)

h,w,_ = im.shape
scale_factor = 2.3

original = np.array(im)
plt.imshow(original,vmin=0)
plt.show()
result = np.zeros((int(scale_factor*h),(int(scale_factor*w)),3), dtype="uint8")
result_h,result_w,_ = result.shape

#result[0:h,0:w,:] = im #Temporary line, you can delete it

#Write code that scales the image by a factor of 2.3
#It should call interpolate.

for i in range(0, result_h):
  y_bwmap = i / scale_factor
  for j in range(0, result_w):
    x_bwmap = j / scale_factor
    if (j / scale_factor) % 1 != 0.0:
      # print("BigShape: " + str(result.shape))
      # print("BigX: " + str(i))
      # print("BigY: " + str(j))
      result[i,j,:] = interpolate(im, y_bwmap, x_bwmap)
    else:
      x_int = int(x_bwmap)
      y_int = int(y_bwmap)
      # print(im[y_int,x_int,:])
      result[i,j,:] = np.multiply(im[y_int,x_int,:],255)
        
plt.imshow(result,vmin=0)
plt.show()

"""## Part 2: Backwards Mapping

Now that we have a interpolation function, we need a function that performs a backward mapping between a source and target image.

Given a simple rotation transformation, **write a function that performs a backwards mapping. This function should also call your interpolate function.**

For this example, the source and target image will be the same size, which means part of your rotated image will be cut off on the corners. You can assume that all pixels need to be backward mapped. Also, **don't forget to invert the transform. This is really easy in numpy.**
"""

#takes in input image and forward transformation, returns output image mapped from input
def backmap1(image, transform):
    h,w,_ = im.shape
    result = np.zeros((h,w,3), dtype="uint8")
    tinv = np.linalg.inv(transform)
    
    #iterate over rows of output image
    for i in range(0,h):
      
      #iterate over columns of output image
      for j in range(0,w):
        current = np.array([[i],[j],[1]])
        origin = np.matmul(tinv,current)
        result[i,j,:] = interpolate(image, origin[0], origin[1])
    
    return result


from math import sin,cos,pi

filename = "test.png"
im = plt.imread(filename)

plt.imshow(im,vmin=0)
plt.show()

transform = np.matrix([[cos(45 * pi/180), -sin(45 * pi/180), w/2],[sin(45 * pi/180),cos(45 * pi/180),-h/5],[0,0,1]])

result = backmap1(im,transform)

plt.imshow(result,vmin=0)
plt.show()

"""## Part 3: Homographies

Now that we have the two specific functions that we need, let's start looking at some more interesting image warping. In class, we discussed how we can use homographies to warp images nonlinearly. In this lab, we have provided the homography generating code for you. 
"""

class Point():
    def __init__(self,x,y):
        self.x = x
        self.y = y


def getHomography(s0,s1,s2,s3,t0,t1,t2,t3):

    x0s = s0.x
    y0s = s0.y
    x0t = t0.x
    y0t = t0.y

    x1s = s1.x
    y1s = s1.y
    x1t = t1.x
    y1t = t1.y

    x2s = s2.x
    y2s = s2.y
    x2t = t2.x
    y2t = t2.y

    x3s = s3.x
    y3s = s3.y
    x3t = t3.x
    y3t = t3.y

    #Solve for the homography matrix
    A = np.matrix([
            [x0s, y0s, 1, 0, 0, 0, -x0t*x0s, -x0t*y0s],
            [0, 0, 0, x0s, y0s, 1, -y0t*x0s, -y0t*y0s],
            [x1s, y1s, 1, 0, 0, 0, -x1t*x1s, -x1t*y1s],
            [0, 0, 0, x1s, y1s, 1, -y1t*x1s, -y1t*y1s],
            [x2s, y2s, 1, 0, 0, 0, -x2t*x2s, -x2t*y2s],
            [0, 0, 0, x2s, y2s, 1, -y2t*x2s, -y2t*y2s],
            [x3s, y3s, 1, 0, 0, 0, -x3t*x3s, -x3t*y3s],
            [0, 0, 0, x3s, y3s, 1, -y3t*x3s, -y3t*y3s]
        ])

    b = np.matrix([
            [x0t],
            [y0t],
            [x1t],
            [y1t],
            [x2t],
            [y2t],
            [x3t],
            [y3t]
        ])

    #The homography solutions a-h
    solutions = np.linalg.solve(A,b)

    solutions = np.append(solutions,[[1.0]], axis=0)

    #Reshape the homography into the appropriate 3x3 matrix
    homography = np.reshape(solutions, (3,3))
    
    return homography

def getScreen():
    result = []
    screen = np.loadtxt("screen.txt")
    for line in screen:
        result.append(Point(int(line[0]), int(line[1])))
    return result

"""We want to be able to get a new image into the tv set in the image shown below. Note that not all pixels will need to be backward mapped. For this reason, we also need to specify a list of points that we are considering. This is provided in the getScreen function definined above.

**Rewrite your backmap function to allow for two images of different sizes and a specific set of points that need to be mapped.**
"""

def backmap2(source, target, transform, points):
    tinv = np.linalg.inv(transform)
    result = np.copy(target)
    for point in points:
      current = np.array([[point.x],[point.y],[1]])
      origin = np.matmul(tinv,current)
      result[point.y,point.x,:] = interpolate(source, origin[1], origin[0])
    
    return result



filename = "test.png"
im = plt.imread(filename)

h,w,_ = im.shape
        
s0 = Point(0,0)
s1 = Point(w-1,0)
s2 = Point(w-1,h-1)
s3 = Point(0,h-1)

t0 = Point(245,152)
t1 = Point(349,150)
t2 = Point(349,253)
t3 = Point(246,261)

tv = plt.imread('tv.jpg')
plt.imshow(tv,vmin=0)
plt.show()

transform = getHomography(s0,s1,s2,s3,t0,t1,t2,t3)

screen = getScreen()

result = backmap2(im, tv, transform, screen)

plt.imshow(result,vmin=0)
plt.show()

"""## Part 4: Geometric Tests

We have a pretty robust warping algorithm now, but we need a way of determining which pixels are of interest and which pixels are not of interest on our target image.

Notice in the image below that we were able to replace the nearest canvas with a picture of BYU campus. We did so by finding the corners of the canvas, determining points that lie inside that canvas, and then using a homography as our transform for the backward mapping. We left a blank canvas for you to try this out as well. 

**Rewrite your backmap function (yet again) to take in the corners of interest, perform a homography, and include a pixel tester that makes a bounding box around the area of interest, then uses cross product geometric testing to verify if a pixel is on the canvas** (we acknowledge there are other ways you could solve this problem, but this is good practice).

"""

def getCanvas(t0, t1, t2, t3):
    canvas = []

    _t0 = np.array([[t0.x], [t0.y], [0]])
    _t1 = np.array([[t1.x], [t1.y], [0]])
    _t2 = np.array([[t2.x], [t2.y], [0]])
    _t3 = np.array([[t3.x], [t3.y], [0]])
    corners = [_t0, _t1, _t2, _t3]

    min_x = np.min(np.array([_t0[0], _t1[0], _t2[0], _t3[0]]))
    max_x = np.max(np.array([_t0[0], _t1[0], _t2[0], _t3[0]]))
    min_y = np.min(np.array([_t0[1], _t1[1], _t2[1], _t3[1]]))
    max_y = np.max(np.array([_t0[1], _t1[1], _t2[1], _t3[1]]))

    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            # Check that point is inside canvas
            inside = True
            for i_corner in range(len(corners)):
                nextCorner = (i_corner + 1) % len(corners)
                crossProduct = (corners[nextCorner] - corners[i_corner]) @ np.transpose(
                    np.array([[x], [y], [0]]) - corners[i_corner])

                if np.min(crossProduct[:, 2]) < 0:
                    inside = False
                    break

            if inside:
                canvas.append(Point(x, y))

    return canvas


def backmap3(source, target, s0, s1, s2, s3, t0, t1, t2, t3):
    h, w, _ = target.shape
    h_s, w_s, _ = source.shape
    transform = getHomography(s0, s1, s2, s3, t0, t1, t2, t3)
    tinv = np.linalg.inv(transform)
    result = np.copy(target)
    canvas = getCanvas(t0, t1, t2, t3)

    for point in canvas:
        current = np.array([[point.x], [point.y], [1]])
        origin = np.matmul(tinv, current)
        result[point.y, point.x, :] = interpolate(source, origin[1], origin[0]) / 255

        if origin[0] < 0 or origin[0] > h_s or origin[1] < 0 or origin[1] > w_s:
          result[point.y, point.x, :] = target[point.y, point.x, :]

    return result
    

museum = plt.imread('museum.png')
plt.imshow(museum,vmin=0)
plt.show()

filename = "test.png"
parrot = plt.imread(filename)
h,w,_ = parrot.shape
        
s0 = Point(0,0)
s1 = Point(w-1,0)
s2 = Point(w-1,h-1)
s3 = Point(0,h-1)

t0 = Point(268,230)
t1 = Point(349,249)
t2 = Point(347,361)
t3 = Point(267,363)

result = backmap3(parrot,museum,s0,s1,s2,s3,t0,t1,t2,t3)
    
plt.imshow(result,vmin=0)
plt.show()