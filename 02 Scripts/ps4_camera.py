import numpy as np
import cv2

from tiff_file_structure import * # TODO change this

'''
    Note 1: Must load C:\Users\Alexander\OneDrive\06 Stereo Camera Set Up\02 Software\02 C Driver Code\OrbisEyeCam\bin\OrbisEyeCameraFirmwareLoader.exe before running script
   Note 2: Potential https://github.com/bensondaled/pseyepy/blob/master/pseyepy/cameras.pyx 
'''

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Display the resulting frame
        cv2.imshow('frame',frame)
        char = cv2.waitKeyEx(10) & 0xFF
        if char == ord('q'):
            break
        elif char == ord('s'): # Save
            print("saving image")

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()