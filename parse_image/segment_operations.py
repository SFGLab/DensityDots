#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zparteka
"""

import numpy as np
from tifffile import tifffile
from operations.point_converter import savePointsAsPdb
from os import path

#todo class statistic writer
def read_segmentation_data_npy(segfile):
    """Read segmentation data from a .npy file (zyx format)"""
    segments = np.load(segfile)
    img = np.swapaxes(segments, 0, 2)
    return img


def read_segmentation_data_tiff(segfile):
    """Read segmentation data from a .tiff file (zyx format)"""
    a = tifffile.imread(segfile)
    img = np.swapaxes(a, 0, 2)
    print(img.shape)
    return img


def split_points_to_segments(segments, points):
    """Apply segemntation to identified points."""
    no_segments = max(np.unique(segments))
    points_in_segments = []
    for i in range(1, no_segments + 1):
        single_seg = []
        for j in range(len(points)):
            if segments[points[j][0]][points[j][1]][points[j][2]] == i:
                single_seg.append(points[j])
        points_in_segments.append(single_seg)
    return points_in_segments


def save_segments(segments, filename_base):
    """Save all segments in separate .pdb files."""
    for i in range(len(segments)):
        filename = filename_base + "_segment_" + str(i + 1) + ".pdb"
        savePointsAsPdb(points=segments[i], filename=filename, connect=False)


def number_of_points_in_segment(segmented_points):
    """Return s dictionary {segmentnumber:numberofpoints}"""
    seg_dict = {}
    for i in range(len(segmented_points)):
        seg_dict[i + 1] = len(segmented_points[i])
    return seg_dict


def save_segments_statistics(filename_base, img, minsize, minvalue, maxvalue, stepsize, number_of_points, spacing,
                             segmented_points):
    """Save basic statistics plus information about segments"""
    seg_dict = number_of_points_in_segment(segmented_points=segmented_points)
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
    stats.write("Number of segments: " + str(len(seg_dict.keys())) + "\n")
    stats.write("Points in segments:" + "\n")
    for i in seg_dict.keys():
        stats.write("\t" + "Segment " + str(i) + ": " + str(seg_dict[i]) + "\n")
    stats.close()
