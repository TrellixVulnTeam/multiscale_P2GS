"""
Mueller matrix polarimetry takes many different images of the same
sample using different input and output polarizations.  Changing the
output polarization on the instrument we are using changes the
optical path, and thus shifts the images.

This script is intended to register the images onto each other and
find a universal transform so that it can be applied to all future
images from the same source.  This will let us get better results with
the final Mueller image.
"""
import mp_img_manip.itk.registration as reg

import javabridge
import bioformats as bf
import SimpleITK as sitk
from pathlib import Path
import os
import pandas as pd

import mp_img_manip.itk.transform as tran
import mp_img_manip.utility_functions as util


def czi_timepoint_to_sitk_image(path_file, position, resolution):
        """
        Open a timepoint from a czi image and make it into an ITK image
        
        :param path_file: Path to the czi file
        :param position: Timepoint to open
        :param resolution: Resolution of the czi image in microns
        :return: A SimpleITK image made from the timepoint
        """
        array = bf.load_image(str(path_file), t=position)
        image = sitk.GetImageFromArray(array)
        image.SetSpacing([resolution, resolution])
        
        return image


def idx_dictionary():
        """Map the polarization state inputs and output states to the t slice from the channel"""
        idx_of_outputs = {
                'Hout': [0, 6, 9, 14],
                'Bout': [1, 7, 8, 15],
                'Pout': [2, 5, 10, 13],
                'Vout': [4, 3, 11, 12],
                'Rout': [18, 19, 20, 17],
                'Lout': [23, 22, 21, 16]}
        
        idx_of_inputs = {
                'Hin': [0, 1, 2, 3, 18, 23],
                'Pin': [6, 7, 5, 19, 22],
                'Vin': [9, 8, 10, 11, 20, 21],
                'Rin': [14, 15, 13, 12, 17, 16]
        }
        
        idx_dict = {'Outputs': idx_of_outputs, 'Inputs': idx_of_inputs}
        
        return idx_dict


def calculate_transforms(path_img: Path, resolution, registration_method, skip_finished_transforms=True):
        """
        Register based on output polarization state, and save the resulting transform
        :param path_img: path to the image file being used to calculate the transforms
        :param resolution: resolution of the image file
        :param registration_method: itk construct holding registration parameters
        :param skip_finished_transforms: whether to skip finding transforms if they already exist or not
        :return:
        """
        idx_dict = idx_dictionary()
        slices_to_register = []
        keys = []
        dict_outputs = idx_dict['Outputs']
        for key in dict_outputs:
                keys.append(key)
                slices_to_register.append(dict_outputs[key][0])
        
        fixed_img = czi_timepoint_to_sitk_image(path_img, slices_to_register[0], resolution)
        
        for idx in range(1, len(slices_to_register)):
                registered_path = Path(path_img.parent, keys[idx] + '.tfm')
                initial_transform = tran.read_initial_transform(registered_path, sitk.AffineTransform)
                
                if skip_finished_transforms:
                        if registered_path.is_file():
                                continue
                
                print('Registering {0} to {1}'.format(keys[idx], keys[0]))
                
                moving_img = czi_timepoint_to_sitk_image(path_img, slices_to_register[idx], resolution)
                
                registered_img, origin, transform, metric, stop = reg.supervised_register_images(
                        fixed_img, moving_img,
                        registration_method=registration_method,
                        initial_transform=initial_transform
                )
                
                tran.write_transform(registered_path, transform)


def transform_polarization_state(path_image, dir_output, resolution, list_positions, state):
        """
        Apply transform to all timepoints with specified output polarization state
        :param path_image: path to the czi image file
        :param dir_output: directory to write the output to
        :param resolution: resolution of the image file
        :param list_positions: list of the timepoints corresponding to output polarization state
        :param state: string of the polarization state
        :return:
        """
        fixed_image = czi_timepoint_to_sitk_image(path_image, 0, resolution)
        
        for position in list_positions:
                output_path = Path(dir_output, path_image.stem + '_' + str(position+1) + '.tif')
                
                if output_path.is_file():
                        continue
                
                moving_image = czi_timepoint_to_sitk_image(path_image, position, resolution)
                
                if state == 'Hout':
                        sitk.WriteImage(moving_image, str(output_path))
                else:
                        transform_path = Path(dir_output, state + '.tfm')
                        registered_image = tran.apply_transform(fixed_image, moving_image, str(transform_path))
                        sitk.WriteImage(registered_image, str(output_path))


def apply_transforms(path_image, dir_output, resolution):
        """
        Apply pre-calculated transforms onto a single mueller polarimetry image
        
        :param path_image: path to the image being processed
        :param dir_output: directory to save the image to
        :param resolution: resolution of the image file
        :return:
        """
        idx_dict = idx_dictionary()
        output_dict = idx_dict['Outputs']
        for state in output_dict:
                transform_polarization_state(path_image, dir_output, resolution, output_dict[state], state)


def bulk_apply_transforms(dir_input, dir_output, resolution, skip_finished_transforms=True):
        """
        Apply pre-calculated transforms onto a whole directory of mueller polarimetry images
        
        :param dir_input: Directory holding both images and the transforms.csv file
        :param dir_output: Directory to write resulting images to
        :param resolution: Resolution of the image files
        :param skip_finished_transforms: Whether to skip applying the transform if files already exist
        :return:
        """
        file_list = util.list_filetype_in_dir(dir_input, 'czi')
        for file in file_list:
                dir_output_file = Path(dir_output, file.stem)
                os.makedirs(dir_output_file, exist_ok=True)
                
                apply_transforms(file, dir_output_file, resolution)


javabridge.start_vm(class_path=bf.JARS, max_heap_size='8G')

mhr_path = Path(r'F:\Research\Polarimetry\Data 01 - Raw and imageJ proccessed images\Mueller raw\1045- slide 1.czi')
mlr_resolution = 2.016
mhr_resolution = 0.81

registration_method = reg.define_registration_method(scale=2, learning_rate=5, iterations=100)

calculate_transforms(mhr_path, mhr_resolution, registration_method)

apply_transforms(mhr_path, mhr_path.parent, mhr_resolution)


javabridge.kill_vm()


