

#=========================
# extract function
#=========================
# cython: boundscheck=False, wraparound=False

import numpy as np
cimport numpy as np 
import pandas as pd
import itertools
import datetime
from libc.math cimport ceil, floor

cdef double[:, :] to_numpy_c(array):
    return np.asarray(array)

cdef double[:] min_values_c(double[:, :] coordinates):
    return np.min(coordinates, axis=0)

cdef double[:] max_values_c(double[:, :] coordinates):
    return np.max(coordinates, axis=0)

cdef int[:] dim_c(double[:, :] coordinates, double voxel_size):
    min_values = min_values_c(coordinates)
    max_values = max_values_c(coordinates)
    return np.ceil((max_values - min_values) / voxel_size).astype(int)

cdef np.ndarray[np.uint8_t, ndim=3] voxels_c(double[:, :] coordinates, double voxel_size, int[:, :] indices):
    min_values = min_values_c(coordinates)
    dim = dim_c(coordinates, voxel_size)
    voxels = np.zeros(dim, dtype=np.uint8)
    voxels[indices[:, 0], indices[:, 1], indices[:, 2]] = 1
    return voxels

cdef int[:, :] indices_c(double[:, :] coordinates, double voxel_size):
    min_values = min_values_c(coordinates)
    return np.floor((coordinates - min_values) / voxel_size).astype(int)

cdef np.ndarray[np.uint8_t, ndim=1] enclosed_c(np.ndarray[np.uint8_t, ndim=3] voxels, int[:, :] indices):
    enclosed = np.full(indices.shape[0], 1, dtype=np.uint8)
    for i in range(indices.shape[0]):
        x, y, z = indices[i]
        surrounding = [(x+dx, y+dy, z+dz) for dx, dy, dz in itertools.product([-1, 0, 1], repeat=3) 
                       if abs(dx) + abs(dy) + abs(dz) == 1]
        for i, j, k in surrounding:
            if 0 <= i < voxels.shape[0] and 0 <= j < voxels.shape[1] and 0 <= k < voxels.shape[2]:
                if not voxels[i, j, k]:
                    enclosed[i] = 0
                    break
    return enclosed

def process_data_cython(pdbdata, voxel_size):
    extractstart=datetime.datetime.now()
    print ("extract start time: "+str(extractstart))

    coordinates = to_numpy_c(pdbdata[['X', 'Y', 'Z']])
    print(coordinates)
    print(coordinates.shape)

    min_values = min_values_c(coordinates)
    print(min_values)

    max_values = max_values_c(coordinates)
    print(max_values)

    indices = indices_c(coordinates, voxel_size)
    voxels = voxels_c(coordinates, voxel_size, indices)
    print(voxels.shape)

    print("indices")
    print(indices.shape)
    print(indices.min(axis=0))
    print(indices.max(axis=0))

    in_voxel_coordinates = np.array([coordinates[i] for i in range(len(coordinates)) if voxels[tuple(indices[i])]])
    in_voxel_indices = np.array([indices[i] for i in range(len(indices)) if voxels[tuple(indices[i])]])
    coordinates_voxelindex_data = np.hstack((in_voxel_coordinates, in_voxel_indices))

    coordinates_voxelindex = pd.DataFrame(coordinates_voxelindex_data , columns=['X', 'Y', 'Z', 'index_x', 'index_y', 'index_z'])
    print(coordinates_voxelindex)

    coordinates_voxelindex['enclosed'] = enclosed_c(voxels, indices).astype(bool)
    atom_types = pdbdata['Atom Name']

    for index, row in coordinates_voxelindex.iterrows():
        coordinates_voxelindex.loc[index, 'Atom Name'] = atom_types[index]

    coordinates_voxelindex = coordinates_voxelindex[~coordinates_voxelindex['enclosed']]
    atom_colors = coordinates_voxelindex['Atom Name']

    extractend=datetime.datetime.now()
    print ("extract end time: "+str(extractend))
    print ("extract time: "+str(extractend-extractstart))

    return coordinates_voxelindex
