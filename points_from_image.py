#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zparteka
"""

import argparse
from parse_image.extract_points import search, read_cmap_image, read_tiff_image, run_multistep_analysis, statistics, \
    apply_spacing, apply_spacing_on_segments
from operations.point_converter import savePointsAsPdb
from parse_image.segment_operations import read_segmentation_data_npy, read_segmentation_data_tiff, \
    split_points_to_segments, save_segments, save_segments_statistics
from os import path


def main():
    parser = argparse.ArgumentParser(description="description")
    parser.add_argument('-i', '--image', help="Image file in *.cmap or *.tiff format.")
    parser.add_argument('-o', '--outpath', help="Where to save your results.", default='./')
    parser.add_argument('-a', '--save_all', type=bool, default=False, help="If True save all sets of points in separate"
                                                                           " .pdb files. Not available for multithread.")
    parser.add_argument('-v1', '--min_value', type=int, default=10, help="Minimal voxel brightness value.")
    parser.add_argument('-v2', '--max_value', type=int, default=None, help="Maximal voxel brightness value.")
    parser.add_argument('-m', '--min_size', type=int, default=2, help="Minimal connected component size.")
    parser.add_argument('-p', '--step_size', type=int, default=10, help="Brightness step size."
                        )
    parser.add_argument('-s', '--singlestep', type=int, default=None, help="Integer value. If not None perform single "
                                                                           "step analysis using given brightness value "
                                                                           "and save results.")
    parser.add_argument('-b', '--save_stats', type=bool, default=True, help="Save file with statistics if True.")
    parser.add_argument('-t', '--threads', type=int, default=1)
    parser.add_argument('-seg', '--segments', type=str, default=None,
                        help="File in .npy or .tiff format with 3d matrix representing image transformation.")
    args = parser.parse_args()

    filename_base = path.join(args.outpath + path.basename(args.image[:-5]))
    if args.image.endswith(".cmap"):
        image_info = read_cmap_image(args.image)
    elif args.image.endswith(".tiff"):
        image_info = read_tiff_image(args.image)
    else:
        return "Wrong image format."

    spacing = image_info[2]
    max_bright = image_info[1]
    image = image_info[0]

    if args.max_value:
        max_brightness = int(args.max_value + 10)
    else:
        max_brightness = int(max_bright + 10)

    if args.singlestep:
        points = search(img=image, min_size=args.min_size, min_value=args.singlestep)
        filename = filename_base + "_brightness_" + str(args.singlestep) + ".pbd"

    else:
        points = run_multistep_analysis(img=image, save_all=args.save_all, min_value=args.min_value,
                                        max_value=max_brightness, min_size=args.min_size, step_size=args.step_size,
                                        outname=filename_base, threads=args.threads)

        filename = filename_base + "_all_points.pdb"

    segments = args.segments
    if segments is not None:
        if segments.endswith(".tiff"):
            segments = read_segmentation_data_tiff(segfile=args.segments)
        elif segments.endswith(".npy"):
            segments = read_segmentation_data_npy(segfile=args.segments)
        segmented_points = split_points_to_segments(segments=segments, points=points)
        segmented_points = apply_spacing_on_segments(segmented_points=segmented_points, spacing=spacing)
        save_segments(segments=segmented_points, filename_base=filename_base)
        if args.save_stats:
            save_segments_statistics(filename_base=filename_base, img=image, minsize=args.min_size,
                                     minvalue=args.min_value,
                                     maxvalue=max_bright, stepsize=args.step_size, number_of_points=len(points),
                                     spacing=spacing, segmented_points=segmented_points)
    else:
        if args.save_stats:
            statistics(filename_base=filename_base, img=image, minsize=args.min_size, minvalue=args.min_value,
                       maxvalue=max_bright, stepsize=args.step_size, number_of_points=len(points), spacing=spacing)
    points = apply_spacing(points=points, spacing=spacing)

    savePointsAsPdb(points=points, filename=filename, connect=False)


if __name__ == '__main__':
    main()
