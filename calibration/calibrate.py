import numpy as np
import cv2
import glob

'''===================================================================
    In calibrate.py, we are able to find the camera intrinsic and extrinsic parameters.
    In order to use package cv2, we should set up our python enviornment below or equal to python3.5

    Meaning of results:
    mtx: a 3x3 floating-point camera matrix
    dist:  vector of distortion coefficients
    rvecs: vector of rotation vectors
    tvecs: vector of translation vectors

    More information is on http://docs.opencv.org/2.4.1/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html
   ===================================================================
'''

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 46, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,5,0)
objp = np.zeros((5*8,3), np.float32)
objp[:,:2] = np.mgrid[0:8,0:5].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

'''===================================================================
    We should use our cameara capturing different images with different perspectives.
    We provide several example here to give you a brief understanding.
   ===================================================================
'''

images = glob.glob('./calibrate_image/*.jpg')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (8,5),None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners)

        # Draw and display the corners
        cv2.drawChessboardCorners(img, (8,5), corners,ret)
        cv2.imshow('img',img)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# calibrate the camera with objectpoints and imagepoints
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

# mtx is the camera matrix and a_11 and a_22 are the focal lengths expressed in unit pixels
print(mtx)


'''===================================================================
    Calculate one point in its 3d location
    This part will not be used in this experiment
   ===================================================================
'''
#clean data as array used for cv2.solvePnP function
objectpoints = []
for item in objpoints[0]:
    item = item.tolist()
    objectpoints.append(item)
objectpoints = np.asarray(objectpoints)

imagepoints = []
for item in imgpoints[0]:
    for element in item:
        element = element.tolist()
        imagepoints.append(element)
imagepoints = np.asarray(imagepoints)

#rvec is rotation vector, tvec is translation vector, rmat is rotation matrix
retval, rvec, tvec = cv2.solvePnP(objectpoints, imagepoints, mtx,0)
rmat,_ = cv2.Rodrigues(rvec)
mid_mat = np.hstack((rmat,tvec))
vector = [[0,0,0,1]]
mid_mat = np.vstack((mid_mat,vector))
actual_vector = (np.linalg.inv(mid_mat)).dot([[0],[0],[1],[1]])

#Get the points in 3D reconstruction
points = []
for point in actual_vector[0:3]:
    points.append(sum(point.tolist()))

'''[  1.26467281e+03   0.00000000e+00   7.02519876e+02]
 [  0.00000000e+00   1.26280610e+03   3.78475298e+02]
 [  0.00000000e+00   0.00000000e+00   1.00000000e+00]]

 [[  1.26126718e+03   0.00000000e+00   6.78749888e+02]
 [  0.00000000e+00   1.26535015e+03   3.33121719e+02]
 [  0.00000000e+00   0.00000000e+00   1.00000000e+00]]'''