
cimport numpy as np
import math
import numpy as np




#=========================
# make dilation
#=========================
def dilation(np.float32_t[:] xcoordinate, np.float32_t[:] ycoordinate, np.float32_t[:] zcoordinate, int pixelxdirection, float tipradius, str tipshape, int tipangle):
    cdef np.float32_t[:] xcoordinate_d
    cdef np.float32_t[:] ycoordinate_d
    cdef np.float32_t[:] zcoordinate_d
    xcoordinate_d = (xcoordinate - np.min(xcoordinate)) / 10
    ycoordinate_d = (ycoordinate - np.min(ycoordinate)) / 10
    zcoordinate_d = (zcoordinate - np.min(zcoordinate)) / 10

    cdef int grid_sizex, grid_sizey
    grid_sizex = pixelxdirection
    grid_sizey = math.ceil(pixelxdirection * (np.max(ycoordinate_d) / np.max(ycoordinate_d)))

    s= cal(grid_sizex,grid_sizey)
    #cdef np.float32_t dx, dy
    #dx = np.max(xcoordinate_d) / grid_sizex
    #dy = np.max(ycoordinate_d) / grid_sizey
    return s

    

cdef cal(int grid_sizex, int grid_sizey):
    return grid_sizex+grid_sizey