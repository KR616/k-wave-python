"""
    Using An Ultrasound Transducer As A Sensor Example

    This example shows how an ultrasound transducer can be used as a detector
    by substituting a transducer object for the normal sensor input
    structure. It builds on the Defining An Ultrasound Transducer and
    Simulating Ultrasound Beam Patterns examples.
"""
import os
from tempfile import gettempdir

# noinspection PyUnresolvedReferences
import setup_test
from kwave.kmedium import kWaveMedium
from kwave.ksource import kSource
from kwave.kspaceFirstOrder2D import kspaceFirstOrder2DC
from kwave.ktransducer import *
from kwave.utils.filters import filter_time_series
from tests.diff_utils import compare_against_ref


def test_tvsp_homogeneous_medium_dipole():
    # pathname for the input and output files
    pathname = gettempdir()

    # =========================================================================
    # SIMULATION
    # =========================================================================

    # create the computational grid
    Nx = 128            # number of grid points in the x (row) direction
    Ny = 128            # number of grid points in the y (column) direction
    dx = 50e-3/Nx    	# grid point spacing in the x direction [m]
    dy = dx             # grid point spacing in the y direction [m]
    kgrid = kWaveGrid([Nx, Ny], [dx, dy])

    # define the properties of the propagation medium
    medium = kWaveMedium(sound_speed=1500, density=1000, alpha_coeff=0.75, alpha_power=1.5)

    # create the time array
    kgrid.makeTime(medium.sound_speed)

    # define a single source point
    source = kSource()
    source.u_mask = np.zeros((Nx, Ny))
    source.u_mask[-Nx//4 - 1, Ny//2 - 1] = 1

    # define a time varying sinusoidal  velocity source in the x-direction
    source_freq = 0.25e6   # [Hz]
    source_mag = 2 / (medium.sound_speed * medium.density)
    source.ux = -source_mag * np.sin(2 * np.pi * source_freq * kgrid.t_array)

    # filter the source to remove high frequencies not supported by the grid
    source.ux = filter_time_series(kgrid, medium, source.ux)

    # define a single sensor point
    sensor_mask = np.zeros((Nx, Ny))
    sensor_mask[Nx//4 - 1, Ny//2 - 1] = 1
    sensor = kSensor(sensor_mask)

    # define the acoustic parameters to record
    sensor.record = ['p', 'p_final']

    # set the input settings
    input_filename = f'example_tvsp_homo_di'
    pathname = gettempdir()
    input_file_full_path = os.path.join(pathname, input_filename + '_input.h5')
    input_args = {
        'save_to_disk': True,
        'data_name': input_filename,
        'data_path': gettempdir(),
        'save_to_disk_exit': True
    }


    # run the simulation
    kspaceFirstOrder2DC(**{
        'medium': medium,
        'kgrid': kgrid,
        'source': source,
        'sensor': sensor,
        **input_args
    })

    assert compare_against_ref(f'out_tvsp_homogeneous_medium_dipole', input_file_full_path), 'Files do not match!'
