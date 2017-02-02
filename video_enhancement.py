import cv2
import numpy as np
from matplotlib import pyplot as plt
import os
import math
import imutils
import subprocess
import argparse

def is_video_file(filename):
  video_file_extensions = ('.mp4', '.avi','.mov')

  if filename.endswith((video_file_extensions)):
      return True
  return

def black_spaces(frame):

  return frame

def rotate90old(iframe):

  rows,cols,_ = iframe.shape
  M = cv2.getRotationMatrix2D((cols/2,rows/2),90,1)
  frame = cv2.warpAffine(iframe,M,(cols,rows))

  return frame 

def rotate90(iframe):
  height,width,_ = iframe.shape

  a = np.zeros((width,height,3), 'uint8')
  a[:,:,0]=np.transpose(iframe[:,:,0])
  a[:,:,1]=np.transpose(iframe[:,:,1])
  a[:,:,2]=np.transpose(iframe[:,:,2])
 
  newdimh=width
  newdimw=(width*width)/height
  newim = np.zeros((newdimh,newdimw,3), 'uint8')  
  img_scaled = cv2.resize(a,(newdimw, newdimh), interpolation = cv2.INTER_AREA)  

  img_scaled = cv2.blur(img_scaled,(35,35))
  x_offset=(newdimw-height)/2
  y_offset=0
  img_scaled[y_offset:y_offset+a.shape[0], x_offset:x_offset+a.shape[1]] = a

  return img_scaled 


def get_w_h(width,height):
 
  newdimh=width
  newdimw=(width*width)/height
  
  return newdimw,newdimh 

def stabilize(vidname):
  path=get_path(vidname)
  out=path+'stabilized_'+get_filename(vidname)

  command1='transcode -J stabilize -i '+ vidname
  command2='transcode -J transform --mplayer_probe -i '+ vidname +' -y raw -o '+ out
 
  os.system(command1)
  os.system(command2)
  return  

def denoise(nframe):

  frame = cv2.fastNlMeansDenoisingColored(nframe,None,10,10,7,21)
  #sigma_est = estimate_sigma(nframe, multichannel=True, average_sigmas=True)
  #frame = denoise_wavelet(nframe, multichannel=True)
  #frame = denoise_wavelet(nframe, multichannel=True, convert2ycbcr=True)
  #frame = denoise_bilateral(nframe, sigma_range=0.1, sigma_spatial=15)
  return frame 

def equalize(imgt):
  img0 = imgt[:,:,0]
  img1 = imgt[:,:,1]
  img2 = imgt[:,:,2]

  clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

  cl0 = clahe.apply(img0)
  cl1 = clahe.apply(img1)
  cl2 = clahe.apply(img2)

  imgt[:,:,0]=cl0
  imgt[:,:,1]=cl1
  imgt[:,:,2]=cl2
 
  return imgt

def get_path(vidname):
    l=len(vidname.split('/')[-1])
    path=vidname[0:-l]
    return path 

def get_filename(vidname):
    return  vidname.split('/')[-1]

def get_only_audio(vidname):
  path=get_path(vidname)
  out=path+'audio_'+get_filename(vidname)
  command = 'ffmpeg -i '+ vidname+ ' -ab 160k -ac 2 -ar 44100 -vn '+ out+'.wav'
  subprocess.call(command, shell=True)
  return out

def add_audio(vidname,audiopath):
  path=get_path(vidname)
  out=path+'with_audio_'+get_filename(vidname)
  command='ffmpeg -i ' +vidname+ ' -i '+ audiopath+ ' -vcodec copy -acodec copy '+ out
  subprocess.call(command, shell=True)
  return 

def process_video(vidname,proc_flags):
  if proc_flags['stabilize']:
    stabilize(vidname)
  print  vidname
  cap = cv2.VideoCapture(vidname)

  # Define the codec and create VideoWriter object
  fourcc = cv2.VideoWriter_fourcc(*'XVID')

  vw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  vh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

  fs = cap.get(cv2.CAP_PROP_FPS)
  nof = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

  
  if math.isnan(fs):fs=30

  fs=int(fs)
 
  path=get_path(vidname)

  outname=path+'proccessed_'+get_filename(vidname)

  if proc_flags['rotate90']:
    vw,vh=get_w_h(vw,vh)

  out = cv2.VideoWriter(outname,fourcc, fs, (vw,vh))
  cnt=0
  while(cap.isOpened()):
      ret, frame = cap.read()
      if ret==True:        
          cnt=cnt+1
          #print cnt,nof
          if cnt%10==0:
            print 'frame ',cnt,' of ', nof
          
          if proc_flags['equalize']:
            frame=equalize(frame) 
          if proc_flags['denoise']:
            frame=denoise(frame) 
          if proc_flags['rotate90']:
            frame=rotate90(frame)

          out.write(frame)
         
          if cv2.waitKey(1) & 0xFF == ord('q'):
              break
      else:
          break

  cap.release()
  out.release()
  cv2.destroyAllWindows()

  return

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Video_enhancement')
    parser.add_argument('--dir', dest='root_folder', help='Choose root directory to process',default='/home/')
    parser.add_argument('--equalize', dest='equalize', help='Perform histogram equalization',default=True,type=bool)
    parser.add_argument('--denoise', dest='denoise', help='Perform frame denoising',default=False,type=bool)
    parser.add_argument('--rotate90', dest='rotate90', help='Perform 90 degrees rotation',default=False,type=bool)
    parser.add_argument('--stabilize', dest='stabilize', help='Perform video stabilization ',default=False,type=bool)
    parser.add_argument('--keep_audio', dest='keep_audio', help='Keep video audio',default=False,type=bool)

    args = parser.parse_args()
    return args

if __name__ == '__main__':

 
  args = parse_args()
  root_folder=args.root_folder
  proc_flags={}
  proc_flags['equalize']=args.equalize
  proc_flags['denoise']=args.denoise
  proc_flags['rotate90']=args.rotate90
  proc_flags['stabilize']=args.stabilize

  
  for top, dirs, files in os.walk(root_folder):
   
      for nm in files:       
          vidname=os.path.join(top, nm) 
          print vidname,is_video_file(vidname) 

          if is_video_file(vidname): 
        
            if args.keep_audio:    
              audiopath=get_only_audio(vidname)
            
            process_video(vidname,proc_flags)
            
            if args.keep_audio:
              add_audio(vidname,audiopath)