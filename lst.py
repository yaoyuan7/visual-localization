import numpy as np
import numpy.linalg

'''=====================================
	A unspecial function used to calculate least square model
	Input is A and b, to be mentioned, if the dimension of A is N*M, then the dimension of b should be N*M
	return x value will be N*N
   =====================================
'''
def leastsquare(A,b):
	A_t = np.transpose(A)
	A_comb = np.dot(A_t, A)
	A_inv = np.linalg.inv(A_comb)
	A_fin = np.dot(A_comb, A_t)
	x = np.dot(A_fin,b)

	return x

