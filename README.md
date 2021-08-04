# Bag2Video
Convert binary data from an Intel RealSense LiDAR camera to a video file using OpenCV. Specify frame type to fetch (RGB or depth) and frames per second.

Example usage:

`python bag2video.py -i %file_path0% %file_path1% %file_path2% -t rgb -f 15`

Which will fetch the RGB data from the three filepaths specified and convert them to MP4 files at 15 FPS.
