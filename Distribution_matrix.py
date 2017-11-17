import h5py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, SymLogNorm, PowerNorm
from pylab import *
from math import sin, cos
from collections import OrderedDict as odict
from numpy.linalg import norm
from functools import partial
import sys

def main(data_path,rotation_angle,cutoff_radius):
	'''
	Inputs:
	1.Data path for each HDF5 file of galaxy
	2.rotation_angle [phi,theta,psi] in a python list 
	3.cutoff for the galaxy 


	Return:
	1.A HDF5 file with six matrix distribution and its attributes
	  -star weights
	  -star velocity
	  -star dispersion
	  -gas weight
	  -gas velocity
	  -gas dispersion
	2.To access attributes such as galaxy name/rotation angle/ cutoff radius, one might call as below:
	   /data_hdf5_file/.attrs['galaxy']
	   /data_hdf5_file/.attrs['cutoff_radius']
	   /data_hdf5_file/.attrs['rotation_angle']

	'''
	cutoff_radius = int(cutoff_radius)
	data = h5py.File(data_path,'r')
	PartType0 = data['PartType0'] # Gas particles
	PartType4 = data['PartType4'] # Star particles

	#"[0,0,0]"
	rotation_angle_split = rotation_angle.split(",")


	rotation_angle = np.zeros(3)
	rotation_angle[0] = np.float(rotation_angle_split[0][1:])
	rotation_angle[1] = np.float(rotation_angle_split[1])
	rotation_angle[2] = np.float(rotation_angle_split[2][:-1])




	def construct_rotation_matrix(rotation_angle):

	    '''
	    Construct rotation matrix based on Euler angles
	    Reference: http://mathworld.wolfram.com/EulerAngles.html
	    
	    Param: rotation_angle [phi, theta, psi] in python list
	    return: rotation_matrix in numpy array, shape (3,3)
	    '''
	    # Extract Euler angle

	    phi, theta, psi = rotation_angle
	    # Construct rotation matrix in numpy array
	    rotation_matrix = np.array(
	(
	    (cos(psi)*cos(phi)-cos(theta)*sin(phi)*sin(psi) , cos(psi)*sin(phi)+cos(theta)*cos(phi)*sin(psi) , sin(psi)*sin(theta)) , 
	(-sin(psi)*cos(phi)-cos(theta)*sin(phi)*cos(psi) , -sin(psi)*sin(phi)+cos(theta)*cos(phi)*cos(psi) , cos(psi)*sin(theta)) ,
	(sin(theta)*sin(phi) , -sin(theta)*cos(phi) , cos(theta))
	)
	    )
	    return rotation_matrix



	def rotate_batch_coordinates(rotation_angle, coordinates):
	    '''
	    Rotate batch of coordinates
	    param rotation_angle: [phi, theta, psi] in python list
	    param coordinates: Batch coordinates in numpy array shape (N, 3)
	    return: Rotated coordinates in numpy array shape (N, 3)
	    '''
	    rotation_matrix = construct_rotation_matrix(rotation_angle)
	    return rotation_matrix.dot(coordinates.T).T


	def get_rotated_coordinates(data,  rotation_angle, cutoff_radius):
	    
	    
	    # Filter: Cut off distance
	    gas_filter = np.where(norm(PartType0['Coordinates'][:], axis=1)<cutoff_radius)[0]
	    # Gas, get coordinates StarFormationRate and Velocities
	    gas_dict = odict([
	        ('Coordinates', rotate_batch_coordinates(rotation_angle, PartType0['Coordinates'][:][gas_filter])),
	        ('weights', PartType0['StarFormationRate'][:][gas_filter].reshape(-1)), 
	        ('Velocities', rotate_batch_coordinates(rotation_angle, PartType0['Velocities'][:])[gas_filter])
	    ])
	    
	    # Filter: For stars, GFM_StellarFormationTime should be greater than zero to be considered.
	    star_filter = np.where(
	        (PartType4['GFM_StellarFormationTime'][:].reshape(-1)>0)&
	        (norm(PartType4['Coordinates'][:], axis=1)<cutoff_radius)
	                          )[0]
	    # Stars, get coordinates masses Velocities and GFM_StellarFormationTime
	    star_dict = odict([
	        ('Coordinates', rotate_batch_coordinates(rotation_angle, PartType4['Coordinates'][:][star_filter])),
	        ('weights', PartType4['Masses'][:][star_filter].reshape(-1)),
	        ('Velocities', rotate_batch_coordinates(rotation_angle, PartType4['Velocities'][:][star_filter]))
	    ])
	    
	    return gas_dict, star_dict



	def get_weights_dist2D(particle_dict):
	    weights_dist, xedges, yedges = np.histogram2d(x=particle_dict['Coordinates'][:, 0], 
	                                                  y=particle_dict['Coordinates'][:, 1],
	                                                  bins=100,
	                                                  weights=particle_dict['weights']
	                                                 )
	    return weights_dist, xedges, yedges

	def get_velocity_dist2D(particle_dict, weights_dist):
	    n_bins = weights_dist.shape[0]
	    velocities_dist, xedges, yedges = np.histogram2d(x=particle_dict['Coordinates'][:, 0], 
	                                                     y=particle_dict['Coordinates'][:, 1],
	                                                     weights=particle_dict['weights']*particle_dict['Velocities'][:, 2], 
	                                                     bins=n_bins
	                                                    )
	    return np.nan_to_num(velocities_dist/weights_dist)
	    #return velocities_dist

	def get_dispersion_dist2D(particle_dict, weights_dist):
	    n_bins = weights_dist.shape[0]
	    x,y,z = particle_dict['Coordinates'].T
	    vx, vy, vz = particle_dict['Velocities'].T
	    particle_counts,xedges,yedges = np.histogram2d(x, y, bins=n_bins)
	    vz_sum, _, _ = np.histogram2d(x, y, weights = vz, bins=n_bins)
	    for edges in [xedges, yedges]:
	        edges[0] = round(edges[0])-1
	        edges[-1] = round(edges[-1])
	    vz_bin_x = np.digitize(x, xedges)-1
	    vz_bin_y = np.digitize(y, yedges)-1
	    vz_avgs_hist = np.divide(vz_sum, particle_counts, where=particle_counts>0)
	    vz_avgs_arr = vz_avgs_hist[vz_bin_x, vz_bin_y]
	    diff_sq = (vz-vz_avgs_arr)**2
	    dispersion_dist,_,_ = np.histogram2d(x, y,weights = particle_dict['weights'][:]*diff_sq, bins=n_bins)
	    return np.nan_to_num(dispersion_dist/ weights_dist)


	gas_dict, star_dict = get_rotated_coordinates(data, rotation_angle, cutoff_radius) 
	star_weights_dist, xedges, yedges = get_weights_dist2D(star_dict)
	star_velocity_dist = get_velocity_dist2D(star_dict,star_weights_dist)
	star_dispersion_dist = get_dispersion_dist2D(star_dict, star_weights_dist)


	gas_weights_dist, xedges, yedges = get_weights_dist2D(gas_dict)
	gas_velocity_dist = get_velocity_dist2D(gas_dict,star_weights_dist)
	gas_dispersion_dist = get_dispersion_dist2D(gas_dict, star_weights_dist)

	galaxy_name = data_path.split("/")[-1]
	galaxy_name = galaxy_name.split(".")[0]



	h5f = h5py.File('data.hdf5', 'w')

	h5f.create_dataset('star_weights_dist', data=star_weights_dist)
	h5f.create_dataset('star_velocity_dist', data=star_velocity_dist)
	h5f.create_dataset('star_dispersion_dist', data=star_dispersion_dist)

	h5f.create_dataset('gas_weights_dist', data=gas_weights_dist)
	h5f.create_dataset('gas_velocity_dist', data=gas_velocity_dist)
	h5f.create_dataset('gas_dispersion_dist', data=gas_dispersion_dist)


	h5f.attrs['galaxy'] = galaxy_name
	h5f.attrs['rotation_angle'] = rotation_angle
	h5f.attrs['cutoff_radius'] = cutoff_radius

	h5f.close()




if __name__ == '__main__':
	'''
	Read 1.file path 2.rotation anle 3.cutoff)radisu from terminal
	'''

	data_path = sys.argv[1]
	rotation_angle = sys.argv[2]
	cutoff_radius = sys.argv[3]

	main(data_path,rotation_angle,cutoff_radius)














