# vid-enh
Video quality enhancement


Prerequisites

Python OpenCV (use these instructions http://rodrigoberriel.com/2014/10/installing-opencv-3-0-0-on-ubuntu-14-04/)

sudo pip install imutils

sudo apt-get install mplayer

sudo pip install numpy

sudo pip install matplotlib


Example of use

python video_enhancement.py --dir /home/user/Videos --equalize True

python video_enhancement.py --help

usage: video_enhancement.py [-h] [--dir ROOT_FOLDER] [--equalize EQUALIZE]
                            [--denoise DENOISE] [--rotate90 ROTATE90]
                            [--stabilize STABILIZE] [--keep_audio KEEP_AUDIO]

Video_enhancement

optional arguments:
  -h, --help            show this help message and exit
  --dir ROOT_FOLDER     Choose root directory to process
  --equalize EQUALIZE   Perform histogram equalization
  --denoise DENOISE     Perform frame denoising
  --rotate90 ROTATE90   Perform 90 degrees rotation
  --stabilize STABILIZE
                        Perform video stabilization
  --keep_audio KEEP_AUDIO
                        Keep video audio



