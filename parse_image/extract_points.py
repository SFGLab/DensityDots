#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Zofia Parteka
"""
Created on Tue Feb 14 10:53:10 2017

@author: zofia

"""

import tifffile
import numpy as np
import SimpleITK as sitk
import h5py
from os import path
from multiprocessing.dummy import Pool as ThreadPool
from operations.point_converter import savePointsAsPdb


#TODO add segment information to image - how to define the points that should be a connection between images?

def read_cmap_image(image):
    """Load CMAP image and define the spacing and maximal brightness of image"""
    cmap_file = h5py.File(image)
    a = np.array(cmap_file.get("Chimera/image1/data_zyx"))
    spacing = np.array([1, 1, 1])
    try:
        spacing = cmap_file.get("Chimera/image1").attrs["step"]
    except Exception:
        pass
    img = np.swapaxes(a, 0, 2)
    max_bright = img.max()
    return img, max_bright, spacing


def read_tiff_image(image, spacing=[1.0, 1.0, 1.0]):
    """Load TIFF image and define the spacing and maximal brightness of image"""
    a = tifffile.imread(image)[..., 0]
    img = np.swapaxes(a, 0, 2)
    max_bright = img.max()
    spacing = np.array(spacing)
    return img, max_bright, spacing


def search(img, min_size=2, min_value=10):
    """Perform single step of connected component analysis, find the brightest voxels and return points."""
    c = components(img > min_value, min_size)
    # TODO c.max zamiast bincount - analiza zdjecia Reszta/5x5x30/91_nuc21syg1
    compo = np.bincount(c.flat)
    points = []
    mbright = []
    for i in range(1, len(compo)):
        spot = np.nonzero(c == i)
        voxels_per_spot = len(spot[0])
        max_brightness = 0
        max_position = ()
        for j in range(0, voxels_per_spot):
            brightness = img[spot[0][j]][spot[1][j]][spot[2][j]]
            if brightness > max_brightness:
                max_brightness = brightness
                max_position = (spot[0][j], spot[1][j], spot[2][j])
        points.append(tuple(max_position))
        mbright.append(max_brightness)
    return points


def components(image_np, min_size=0):
    """Get connected components from image."""
    if image_np.dtype == np.bool:
        image_np = image_np.astype(np.uint8)
    sim = sitk.GetImageFromArray(image_np)
    com = sitk.ConnectedComponent(sim)
    sort = sitk.RelabelComponent(com, min_size)
    return sitk.GetArrayFromImage(sort)

# TODO numpy.linespace zamiast range
def singlethread(img,  min_value, max_value, min_size, step_size, save_all, outname):
    """Run image analysis step by step using one thread."""
    points = []
    for value in range(min_value, max_value, step_size):
        print("Brightness: " + str(value))
        step_points = (search(img=img, min_size=min_size, min_value=value))
        if save_all:
            if len(step_points) == 0:
                print('No points found for brightness: ' + str(value))
            else:
                points += step_points
                savePointsAsPdb(points=step_points, filename=outname + "_brightness_" + str(value) + ".pdb",
                                connect=False)
        else:
            points += step_points
    points = list(set(list(points)))
    return points


def multithread(img, min_value, max_value, min_size, step_size, threads):
    """Run image analysis parallel on multiple threads. Does not allow saving the results of each step."""
    values_table = []
    for value in range(min_value, int(max_value), step_size):
        values_table.append((img, min_size, value))
    pool = ThreadPool(threads)
    step_points = pool.starmap(search, values_table)
    pool.close()
    pool.join()
    points = list(set(sum(step_points, [])))
    return points


def run_multistep_analysis(img, save_all, min_value, max_value, min_size, step_size, outname, threads):
    """Run multistep connected components analysis on an 3D image based on given minimal value, maximal value
    and step size."""
    max_value += 10
    if threads > 1:
        points = multithread(img=img, min_value=min_value, max_value=max_value, min_size=min_size,
                             step_size=step_size, threads=threads)
    else:
       points = singlethread(img=img, min_value=min_value, max_value=max_value, min_size=min_size,
                     step_size=step_size, save_all=save_all, outname=outname)
    return points


def apply_spacing(points, spacing):
    """Apply voxel spacing from .cmap metadata on identified points."""
    for i in range(len(points)):
        points[i] = tuple(points[i] * spacing)
    return points

#todo  changing source list - change this!
def apply_spacing_on_segments(segmented_points, spacing):
    """Apply voxel spacing from .cmap metadata on identified points."""
    for i in range(len(segmented_points)):
        for j in range(len(segmented_points[i])):
            segmented_points[i][j] = tuple(segmented_points[i][j] * spacing)
    return segmented_points


def statistics(filename_base, img, minsize, minvalue, maxvalue, stepsize, number_of_points, spacing):
    """Save some statistics from the image and the parameters used to run the program."""
    stats_filename = filename_base + "_statistics.txt"
    stats = open(stats_filename, "w")
    stats.write(path.basename(filename_base) + "\n")
    stats.write("Minimal connected component size: " + str(minsize) + "\n")
    stats.write("Minimal brightness (cutoff): " + str(minvalue) + "\n")
    stats.write("Maximal brightness of image: " + str(maxvalue) + "\n")
    stats.write("Step size: " + str(stepsize) + "\n")
    stats.write("Image size (x,y,z): " + str(img.shape) + "\n")
    stats.write("Spacing (x,y,z): " + str(spacing) + "\n")
    stats.write("Points found: " + str(number_of_points) + "\n")
    stats.close()
