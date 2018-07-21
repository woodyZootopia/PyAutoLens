import sys

sys.path.append("../../")
import numpy as np
from src.imaging import mask
from src.pixelization import frame_convolution
from src.analysis import galaxy
from src.profiles import mass_profiles
import time
import os
import numba

path = os.path.dirname(os.path.realpath(__file__))

def load(name):
    return np.load("{}/{}.npy".format(path, name))

grid = load("deflection_data/grid")

psf_shape = (21, 21)

ma = mask.Mask.for_simulate(shape_arc_seconds=(4.0, 4.0), pixel_scale=0.05, psf_size=psf_shape)

grid_data = ma.data_collection_from_image_noise_and_exposure_time(image=np.ones(ma.shape), noise=np.ones(ma.shape),
                                                                   exposure_time=np.ones(ma.shape))
frame = frame_convolution.FrameMaker(mask=ma)
convolver = frame.convolver_for_kernel_shape(kernel_shape=psf_shape)
# This PSF leads to no blurring_coords, so equivalent to being off.
kernel_convolver = convolver.convolver_for_kernel(kernel=np.ones(psf_shape))

repeats = 1

def tick_toc(func):
    def wrapper():
        start = time.time()
        for _ in range(repeats):
            func()

        diff = time.time() - start
        print("{}: {}".format(func.__name__, diff))

    return wrapper

@tick_toc
def current_solution():

    kernel_convolver.convolve_array(grid_data.image)

if __name__ == "__main__":
    current_solution()
