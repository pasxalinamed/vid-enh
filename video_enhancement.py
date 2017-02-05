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


def rotate90old(iframe):

  rows,cols,_ = iframe.shape
  M = cv2.getRotationMatrix2D((cols/2,rows/2),90,1)
  frame = cv2.warpAffine(iframe,M,(cols,rows))

  return frame 


def black_spaces(iframe):
  height,width,_ = iframe.shape

  a=iframe
 
  newdimh=height
  newdimw=int(height*(height*1.0/width*1.0))
  newim = np.zeros((newdimh,newdimw,3), 'uint8')  
  img_scaled = cv2.resize(a,(newdimw, newdimh), interpolation = cv2.INTER_AREA)  
  
  img_scaled = cv2.blur(img_scaled,(75,75))

  x_offset=(newdimw-width)/2
  y_offset=0
  img_scaled[y_offset:y_offset+a.shape[0], x_offset:x_offset+a.shape[1]] = a

  return img_scaled 

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

def get_w_hb(width,height):

  newdimh=height
  newdimw=int(height*(height*1.0/width*1.0))
  
  return newdimw,newdimh 

def get_w_h(width,height):
 
  newdimh=width
  newdimw=(width*width)/height
  
  return newdimw,newdimh 

def stabilizetra(vidname):
  path=get_path(vidname)
  out=path+'stabilized_'+get_filename(vidname)

  command1='transcode -J stabilize -i '+ vidname
  command2='transcode -J transform --mplayer_probe -i '+ vidname +' -y raw -o '+ out
 
  os.system(command1)
  os.system(command2)
  return  

def stabilize(vidname):
 
  path=get_path(vidname)  
  out=path+'temp_'+get_filename(vidname)+'.avi'
  trfname=vidname+'_temp.trf'
  command1='ffmpeg -i '+ vidname +' -vf vidstabdetect=stepsize=6:shakiness=10:accuracy=15:result='+trfname+' -f null - '
  command2='ffmpeg -i '+ vidname +' -vf vidstabtransform=input='+trfname+':zoom=1:smoothing=30,unsharp=5:5:0.8:3:3:0.4 -vcodec libx264 -preset slow -tune film -crf 18 -acodec copy '+out 

  os.system(command1)
  os.system(command2)
  os.remove(trfname)

  return  out

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
  return out+'.wav'

def add_audio(vidname,audiopath):
  path=get_path(vidname)
  out=path+'final_'+get_filename(vidname)
  command='ffmpeg -i ' +vidname+ ' -i '+ audiopath+ ' -vcodec copy -acodec copy '+ out
  subprocess.call(command, shell=True)
  os.remove(audiopath)
  print vidname
  #os.remove(vidname)
  return 

def process_video(vidname,proc_flags):
  flag=False
  if proc_flags['stabilize']:
    vidname=stabilize(vidname)
    flag=True   
  
  cap = cv2.VideoCapture(vidname)  

  vw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  vh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
  fs = cap.get(cv2.CAP_PROP_FPS)
  nof = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
  
  if math.isnan(fs):fs=30

  fs=int(fs)

  path=get_path(vidname)

  outname=path+'final_'+get_filename(vidname)+'.avi'

  if proc_flags['rotate90']:
    vw,vh=get_w_h(vw,vh)
  if proc_flags['rem_black_spaces']:
    vw,vh=get_w_hb(vw,vh)

  fourcc = cv2.VideoWriter_fourcc(*'XVID')
  out = cv2.VideoWriter(outname,fourcc, fs, (vw,vh))
 
  cnt=0
  while(cap.isOpened()):
      ret, frame = cap.read()
     
      if ret==True:        
          cnt=cnt+1
         
          if cnt%10==0:
            print 'frame ',cnt,' of ', nof

          if proc_flags['rem_black_spaces']:
            frame=black_spaces(frame) 
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

  if flag==True:os.remove(vidname)

  return outname

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Video_enhancement')
    parser.add_argument('--dir', dest='root_folder', help='Choose root directory to process',default='/home/')
    parser.add_argument('--equalize', dest='equalize', help='Perform histogram equalization',default=False,type=bool)
    parser.add_argument('--denoise', dest='denoise', help='Perform frame denoising',default=False,type=bool)
    parser.add_argument('--rotate90', dest='rotate90', help='Perform 90 degrees rotation',default=False,type=bool)
    parser.add_argument('--stabilize', dest='stabilize', help='Perform video stabilization ',default=False,type=bool)
    parser.add_argument('--keep_audio', dest='keep_audio', help='Keep video audio',default=False,type=bool)
    parser.add_argument('--rem_black_spaces', dest='rem_black_spaces', help='rem_black_spaces',default=False,type=bool)

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
  proc_flags['rem_black_spaces']=args.rem_black_spaces

  if proc_flags['stabilize']==True and proc_flags['rotate90']==True:
    proc_flags['rotate90']=False
    proc_flags['rem_black_spaces']=True

  
  for top, dirs, files in os.walk(root_folder):
   
      for nm in files:    
          nm='DVD1.mp4'
          vidname=os.path.join(top, nm)     
          print vidname      

          if is_video_file(vidname): 
        
            if args.keep_audio:    
              audiopath=get_only_audio(vidname)            
           
            out_name=process_video(vidname,proc_flags)            

            if args.keep_audio:        
              add_audio(out_name,audiopath)
print 'End!'
            
