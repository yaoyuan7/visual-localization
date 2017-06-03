import math
import cv2
import urllib.request
import numpy as np
import os

'''===================================================================
    In getimage.py, we are able to read and save images by our webcams.
    This program will capture images with a short interval until taking 20 pictures.
    So please move the cameara quickly and stably. 

    Also, we can take the picture one  by one by running this program one after another.
   ===================================================================
'''

def get_image(n):
    #get image from webcam stream and save it in folder apriltags/calibrate_image/*.jpg
    #url form: "http://172.16.156."+str(n)+":8080/?action=stream"

    stream = urllib.request.urlopen('http://172.16.156.'+str(n)+':8080/?action=stream'.format(n))
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
           #if cv2.waitKey(1) == 27:
            #   exit(0)

if __name__ == '__main__':

    output = 'test'
    calibrate = 'calibrate'
    if not os.path.exists(output):
        os.makedirs(output)

    for i in range(0,1):
        img=get_image(139)
        cv2.imwrite('{0}/input_{1}_{2}.jpg'.format(output,139,i),img)
        img=get_image(141)
        cv2.imwrite('{0}/input_{1}_{2}.jpg'.format(output,141,i),img)
        img=get_image(145)
        cv2.imwrite('{0}/input_{1}_{2}.jpg'.format(output,145,i),img)
        cv2.waitKey(200)
