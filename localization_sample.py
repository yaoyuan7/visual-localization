import re
import subprocess
import math
import cv2
import urllib.request
import json
import time
import os
from numpy import *
import numpy as np
from camera import camera
from ast import literal_eval
from scipy.optimize import nnls 

'''===========================================================
	This program is a sample of localization.py under the same folder.
	In this program, you don't need to connect to the webcam and you are
	able to measure the data information from an image located in the same folder.
   ===========================================================
'''

def coordinate_matrix(tag_location,tags):
	# compute the coordinate matrix used for transferring cameara frame to global frame
	X = [] 
	for i in range(0,len(tags)):
		X.append(tags[i][2])
		X.append(tags[i][3])
		X.append(tags[i][4])
		X.append(1)
	#form of X is like (x,y,z,1,x,y,z,1...)
	X = np.array(X)
	X = X.reshape((len(tags),4)) #X is N*4

	#search for the locations of tags in global frame according to tags_location
	tag_list = []
	for i in range(0,len(tags)):
		tag_list.append(tags[i][0])

	tag_sorted_location = tag_location
	mapping = dict((x[0], x[1:])for x in tag_location)
	tag_sorted_location[:] = [[x,] + mapping[x] for x in tag_list]
	print(tag_sorted_location)
	#tag_sorted_location = sorted(tags, key=lambda x: x[0])
	b = []
	for i in range(0, len(tag_sorted_location)):
		b.append(tag_sorted_location[i][1])
		b.append(tag_sorted_location[i][2])
		b.append(tag_sorted_location[i][3])
		b.append(1)
	#form of b is (x,y,z,1,x,y,z,1......)
	b = np.array(b)
	b = b.reshape((len(tag_sorted_location),4)) #b is N*4

	A = np.zeros((4,4))
	for i in range(0, 4):
		b_transpose = np.transpose(b)
		b_vector = b_transpose[i]
		a = np.linalg.lstsq(X, b_vector)[0]
		A[i] = a
	
	return A 


if __name__ == '__main__':

	width = 1280
	height = 720
	information = camera.rundemo(width,height,'input141_0.jpg')
	tags = camera.result(information)
	with open('output/tag_location.json') as data_file:    
		tag_location = json.load(data_file)
	matrix = coordinate_matrix(tag_location,tags)
	print(matrix)