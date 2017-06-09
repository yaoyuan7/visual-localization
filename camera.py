#this program has to be used under ~/apriltags/

import re
import subprocess
import math
import cv2
import urllib.request
import numpy as np
'''===========================================================
	This program is used to capture images from a webcam.
	The final data will be saved in json file under the same folder named ./output/*.jpg

	url form is "http://172.16.156."+str(n)+":8080/?action=stream", you are able to test the camera with 
	typing the url in browser.
   ===========================================================
'''
class camera:
	def rundemo(width,height,img):
		#retrieve location information about apriltags from image
		#example: distance=1.19128m, x=0.442468, y=-0.980352, z=-0.512135, yaw=-0.0253801, pitch=-0.000894956, roll=1.98666e-05, cxy=(1649.37, 934.47)
		raw_result = subprocess.Popen(['./apriltags/build/bin/apriltags_demo', '-W', str(width), '-H', str(height),img],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
		result = raw_result.communicate()[0]

		info = result.decode()
		index_begin = info.index('Id')
		final_result = info[index_begin:]
		
		return final_result

	def get_image(n):
		#get image from web camera stream and save it under ~/apriltags/output/*.jpg
		#url form: "http://172.16.156."+str(n)+":8080/?action=stream"

		stream = urllib.request.urlopen('http://172.16.156.{}:8080/?action=stream'.format(n))
		byte = bytes()
		while True:

		    byte += stream.read(1024)
		    a = byte.find(b'\xff\xd8')
		    b = byte.find(b'\xff\xd9')
		    if a != -1 and b != -1:
		        jpg = byte[a:b+2]
		        byte = byte[b+2:]
		        i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
		        cv2.imshow('i', i)

		        return i
	#	        if cv2.waitKey(1) == 27:
	#	            exit(0)

	def data_clean(information):
		#The final result would be like [((1649.37, 934.47), 1.19128)], where the first element is the location of apriltag point 
		#and the second element is the distance from camera to tags
		#get center location
		tag = []
		index = information.index('cxy')
		location = information[index+4:len(information)-1]

		#get distance location
		index_m = information.index('m')
		distance = information[9:index_m]
		#get clean data
		index_left = location.index('(')
		index_right = location.index(')')
		index_mid = location.index(',')
		locationx = location[index_left+1:index_mid]
		locationy = location[index_mid+2:index_right]

		tag.append(((float(locationx),float(locationy)),float(distance)))
		return tag

	def result(information):
		#The final result would be like [(tagid, distance, x, y, z, yaw, pitch, roll)]. x, y, z are in meter; and yaw, pitch, roll are in angle
		result = []
		index_id = []
		index_d = []
		index_x = []
		index_y = []
		index_z = []
		index_yaw = []
		index_pitch = []
		index_roll = []
		index_cxy = []
		for match in re.finditer('Id',information):
			index_id.append(match.end())
		for match in re.finditer('distance',information):
			index_d.append(match.end())
		for match in re.finditer('x=',information):
			index_x.append(match.end())
		for match in re.finditer(', y=',information):
			index_y.append(match.end())
		for match in re.finditer('z=',information):
			index_z.append(match.end())
		for match in re.finditer('yaw',information):
			index_yaw.append(match.end())
		for match in re.finditer('pitch',information):
			index_pitch.append(match.end())
		for match in re.finditer('roll',information):
			index_roll.append(match.end())
		for match in re.finditer('cxy',information):
			index_cxy.append(match.end())

		for i in range(0, len(index_d)):
			tagid = information[index_id[i]+1:index_d[i]-22]
			distance = information[index_d[i]+1:index_x[i]-5]
			x = information[index_x[i]: index_y[i]-4]
			y = information[index_y[i]: index_z[i]-4]
			z = information[index_z[i]: index_yaw[i]-5]
			yaw = information[index_yaw[i]+1: index_pitch[i]-7]
			pitch = information[index_pitch[i]+1: index_roll[i]-6]
			roll = information[index_roll[i]+1: index_cxy[i]-5]
			#print(distance,x,y,z,yaw,pitch,roll)
			result.append((int(tagid),float(distance),float(x),float(y),float(z),float(yaw),float(pitch),float(roll)))
		return result

	def normalization(number, tag, tags, camera_angle):
		if number == 139:
			tags.extend(tag)
		if number == 141:
			for item in tag:
				item_x = item[1]
				item_z = item[3]
				item[3] = item_z*math.cos(camera_angle[0])+item_x*math.sin(camera_angle[0])
				item[1] = -item_z*math.sin(camera_angle[0])+item_x*math.cos(camera_angle[0])

			tags.extend(tag)
		if number == 143:
			for item in tag:
				item_x = item[1]
				item_z = item[3]
				item[3] = item_z*math.cos(camera_angle[0]+camera_angle[1])+item_x*math.sin(camera_angle[0]+camera_angle[1])
				item[1] = -item_z*math.sin(camera_angle[0]+camera_angle[1])+item_x*math.cos(camera_angle[0]+camera_angle[1])

			tags.extend(tag)
		if number == 145:
			for item in tag:
				item_x = item[1]
				item_z = item[3]
				item[3] = item_z*math.cos(camera_angle[0]+camera_angle[1]+camera_angle[2])+item_x*math.sin(camera_angle[0]+camera_angle[1]+camera_angle[2])
				item[1] = -item_z*math.sin(camera_angle[0]+camera_angle[1]+camera_angle[2])+item_x*math.cos(camera_angle[0]+camera_angle[1]+camera_angle[2])

			tags.extend(tag)
		return tags

	def angular(tags):
		angular = []

		for i in range(0, len(tags)):
			for j in range(i+1, len(tags)):
				angle = math.acos((tags[i][2]*tags[j][2]+tags[i][3]*tags[j][3]+tags[i][4]*tags[j][4])/tags[i][1]/tags[j][1])
				angular.append((tags[i][0],tags[j][0],angle))
		
		return angular


if __name__ == '__main__':

	output = 'output'
	print("get images information from stream")
	image_list = [139]
	tags = []
	focal = 1300
	camera_angle = [math.pi, math.pi, math.pi, math.pi] #These are the angle between each camera in an seires of 139,141,143,145

	for number in image_list: 
		img = get_image(number)
		cv2.imwrite('{0}/input{1}.jpg'.format(output,number),img)

		width = len(img[0])
		height = len(img)

		information = rundemo(width,height,'{0}/input{1}.jpg'.format(output,number))
		tag = result(information)
		tags = normalization(number, tag, tags, camera_angle)
		#print(information)
	angular = angular(tags)

	print(tags)
	#print(angular)

    