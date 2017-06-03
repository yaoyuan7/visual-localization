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
	This program is used to localize a webcam's location inside a room.
	The final data will be saved in json file under the same folder named ./output/*time/*.json

	First of all, you are supposed to enter the location of tags inside a room one by one, but 
	you don't need to enter them in order. Location file will also saved in json and be reused.
	Secondly, you should hold your cameara stably and the camera will capture the locations of tags
	in camera frame. Then move your camera and measure as many times as you want. Finally, the results 
	will be saved automatically.

	url form is "http://172.16.156."+str(n)+":8080/?action=stream", you are able to test the camera with 
	typing the url in browser.
   ===========================================================
'''

def tag_input():
	#receive the location of tags by input
	#form of tag_location is like ((id,x,y,z),(id,x,y,z)...)
	tag_location = []
	
	n = int(input('Enter the number of tags'))
	for i in range(0,n):
		tag_id = input('Enter the {}th id of the tag: '.format(i+1))
		location = input('Enter the location of {} tag: '.format(i+1))
		string = '(' + tag_id + ',' + location +')'
		value = literal_eval(string)
		tag_location.append(value)

	return tag_location

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

def get_local_time():
	ISOTIMEFORMAT = '%Y-%m-%d-%H-%M-%S'
	localtime = time.strftime(ISOTIMEFORMAT, time.localtime())

	return localtime
def reference_mat(matrix_set):
	reference = []
	for i in range(0,len(matrix_set)):
		index = '{0}_{1}'.format(matrix_set[i][0],matrix_set[i-1][0])
		ref_mat = np.dot(np.linalg.inv(matrix_set[i][1]),matrix_set[i-1][1])
		reference.append((index, ref_mat))
	return reference

if __name__ == '__main__':
	status = 1
	valid = 1
	output = 'output'
	image_list = [139,141,145]
	camera_angle = [math.pi, math.pi, math.pi, math.pi]
	tags = []
	tag_location = []
	location_set = []
	dict_camera = {}
	dict_result = {}
	focal = 1300

	print('Begin Experiement!')

	while valid == 1:
		command = input('Please choose your next step: t for inputing the location of tags, m for starting camera measurement and end for ending experiement!')
		if command == 't':
			print('Please enter the locations of tags!')
			tag_location = tag_input()
			with open('{0}/tag_location.json'.format(output), 'w') as data_file:
				json.dump(tag_location, data_file)	
			valid = 0	

		elif command == 'm':
			with open('output/tag_location.json') as data_file:    
				tag_location = json.load(data_file)

			if tag_location:
				print('We detect your tag locations!')
				status = 1
				valid = 0
			else:
				print('We cannot detect your tag location!')
				print('Please enter the locations of tags!')
				tag_location = tag_input()
				status = 1
				valid = 0
		elif command == 'end':
			status = 0
			valid = 0
		else:
			print('Please enter a valid command!')

	i = 0
	all_measurement = []

	local_time = get_local_time()
	output_time = 'output/{}'.format(local_time)
	if not os.path.exists(output_time):
		os.makedirs(output_time)
		
	while status == 1:
		measurement_iter = []
		matrix_set = []
		for number in image_list: 
			
			img = camera.get_image(number)
			cv2.imwrite('{0}/input{1}_{2}.jpg'.format(output_time,number,i),img)

			print('Image for camera {0} recorded!'.format(number))
			width = len(img[0])
			height = len(img)
			information = camera.rundemo(width,height,'{0}/input{1}_{2}.jpg'.format(output_time,number,i))
			tags = camera.result(information)
			#The final result would be like [(tagid, distance, x, y, z, yaw, pitch, roll)]
			angular = camera.angular(tags)
			#The set of angles would be like[(tagid_1, tagid_2, angle in radians)]
			tags_label = ['id', 'distance', 'x', 'y', 'z', 'yaw', 'pitch', 'roll']
			with open('output/tag_location.json') as data_file:    
				tag_location = json.load(data_file)
			matrix = coordinate_matrix(tag_location,tags)
			print(matrix)
			origin_point = np.array([0, 0, 0, 1])
			camera_location = matrix.dot(origin_point)
			#input ground truth value
			print('Location for image {0} recorded!'.format(number))
			input_x = float(input('Type your measured value on x axis:'))
			input_y = float(input('Type your measured value on y axis:'))
			input_z = float(input('Type your measured value on z axis:'))

			location_set.append(((camera_location[0], camera_location[1], camera_location[2]), i+1, (input_x,input_y,input_z)))# be like (((x,y,z),iter,(ground_truth)))

			#write tags into json file
			measurement_tag = {}
			ID = []
			measurement = {}

			for iteration in range(0,len(tags)):
				for j in range(0,len(tags[0])):
					measurement_tag.update({'{}'.format(tags_label[j]): tags[iteration][j]})
				ID.append(measurement_tag.copy())
			
			matrix_set.append((number,matrix,location_set[i][0])) #matrix_set is a list containing (number of camera, camera matrix, camera coordinate in global frame)	
			measurement.update({'img_name': 'input{0}_{1}.jpg'.format(number,i)})
			measurement.update({'camera_location': location_set[i][0]})
			measurement.update({'ground_truth': location_set[i][2]})
			measurement.update({'tagid':ID})
			measurement_iter.append(measurement)

		'''reference_measurement = {}
		reference = reference_mat(matrix_set)
		for k in range(0,len(reference)):
			title = reference[k][0]
			reference_measurement.update({'{}'.format(title): reference[k][1].tolist()})
		measurement_iter.append(reference_measurement)	'''
		all_measurement.append(measurement_iter)
		
		i = i + 1
		step = input('Continue or Stop? Please type c for continue or others for stop!')
		if step == 'c':
			status = 1
		else:
			status = 0

	with open('{0}/result.json'.format(output_time), 'w') as dataresult:
		json.dump(all_measurement, dataresult)

	print('End Experiement!')