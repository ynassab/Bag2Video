import pyrealsense2 as rs
import numpy as np
import cv2
import argparse
import os
import moviepy.video.io.ImageSequenceClip as img_seq_clip


def convert2video(filepath, frame_type, rgb_fps):
	
	images_folder = 'frames'
	
	pipeline = rs.pipeline()
	config = rs.config()
	
	rs.config.enable_device_from_file(config, filepath)
	
	if frame_type == 'depth':
		config.enable_stream(rs.stream.depth, rs.format.z16, 30)
		fps = rgb_fps*2
	elif frame_type == 'rgb':
		config.enable_stream(rs.stream.color, rs.format.rgb8, 30)
		fps = rgb_fps

	# start streaming from file
	pipeline.start(config)
	colorizer = rs.colorizer()
	
	print('Collecting frames ...')
	
	last_frame_num = 0
	# save every frame in the BAG file as an image
	while True:
		composite_frame = pipeline.wait_for_frames()
		frame_num = composite_frame.frame_number
		print(f"Current frame count: {frame_num}", end='\r')
		
		# don't loop forever
		if frame_num < last_frame_num:
			print('\n')
			break
		
		if frame_type == 'depth':
			special_frame = composite_frame.get_depth_frame()
		elif frame_type == 'rgb':
			special_frame = composite_frame.get_color_frame()
		
		color_frame = colorizer.colorize(special_frame)
		color_image = np.asanyarray(color_frame.get_data())
		
		# add padding to the frame nums so they appear correctly in alphabetical order
		frame_num_str = str(frame_num)
		while len(frame_num_str) < 7:
			frame_num_str = '0' + frame_num_str # e.g. '000107'
		
		cv2.imwrite(f'{images_folder}/frame{frame_num_str}.jpg', color_image)
		
		last_frame_num = frame_num
	
	# create and save video
	print('Converting frames to MP4 ...')
	image_files = [images_folder+'/'+img for img in os.listdir(images_folder) if img.endswith(".jpg")]
	clip = img_seq_clip.ImageSequenceClip(image_files, fps=fps)
	clip.write_videofile(f'{os.path.splitext(filepath)[0]}_{frame_type}_{fps}fps.mp4')
	
	# delete frame images
	print('Deleting temporary files...')
	for image_file in image_files:
		os.remove(image_file)
	
	print('Done')


if __name__ == '__main__':
	
	acceptable_frame_types = ['depth','rgb']
	frame_types_str = ', '.join(acceptable_frame_types)
	default_rgb_fps = 15
	
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--filepaths', nargs='*', help='Path to the BAG file')
	parser.add_argument('-t', '--types', nargs='*', help=f'Type of data to extract. Options: {frame_types_str}')
	parser.add_argument('-f', '--fps', type=int, default=None, help=f'Frames per second. Default: {default_rgb_fps}')
	args = parser.parse_args()
	
	if not type(args.filepaths) == list:
		args.filepaths = [args.filepaths]
	if not type(args.types) == list:
		args.types = [args.types]
	
	for input in [args.filepaths, args.types]:
		if input in [[], None]:
			print(f'Error: argument {input} was not passed. For help, type --help')
			exit()
	
	for filepath in args.filepaths:
		if os.path.splitext(filepath)[1] != ".bag":
			print(f'Error: {filepath} is not a BAG file')
			exit()
	
	for frame_type in args.types:
		if not frame_type in acceptable_frame_types:
			print('Frame type not recognized. For help, type --help') 
			exit()
	
	if args.fps == None:
		rgb_fps = default_rgb_fps
	else:
		if not type(args.fps) in [int, float]:
			print('A non-numeric FPS value was passed. For help, type --help')
			exit()
		rgb_fps = args.fps
	
	# convert BAG files one by one
	for filepath in args.filepaths:
		for frame_type in args.types:
			convert2video(filepath, frame_type, rgb_fps)
	