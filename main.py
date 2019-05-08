from _future_ import division
#Importing dependencies
import cv2
import numpy as np
import time
import Adafruit_PCA9685
pwm = Adafruit_PCA9685.PCA9685()
servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096
signal=0
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)
  # Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)


#HSV Range for orange  color
lowerbound=np.array([0,100,100])
upperbound=np.array([20,255,255])
#Video Source(0 for WebCam)
cam= cv2.VideoCapture(0)
#PID initialisation
desired_posn = 320#Centre of the video
desired_posn1 = 320
kp=0.6
ki=0.053
kd=0.026
t=0.03
integral=0
integral1=0
previous_error=0
previous_error1=0
while True:
     #Getting image from video
     ret, img=cam.read()
     #Resizing the image to 340x220
     img=cv2.resize(img,(640,640))
     #Smoothning image using GaussianBlur
     imgblurred=cv2.GaussianBlur(img,(5,5),2)
     #Converting image to HSV format
     imgHSV=cv2.cvtColor(imgblurred,cv2.COLOR_BGR2HSV)
     #Masking orange color
     mask=cv2.inRange(imgHSV,lowerbound,upperbound)
     #Removing Noise from the mask
     mask = cv2.erode(mask, None, iterations=2)
     mask = cv2.dilate(mask, None, iterations=2)
     #Extracting contour
     cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_NONE)[1]
    #Drawing Contour
     cv2.drawContours(img,cnts,0,(255,0,0),2)
     #Processing each contour
     for c in cnts:   #source: https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/
      # compute the center of the  maximum area contour
          m=max(cnts,key=cv2.contourArea)#finding the contour with maximum area
          M = cv2.moments(m)
          cX = int(M["m10"] / M["m00"])
          cY = int(M["m01"] / M["m00"])
       # draw the max area contour and center of the shape on the image
          cv2.drawContours(img, [m], -1, (0, 255, 0), 2)
          cv2.circle(img, (cX, cY), 7, (255, 255, 255), -1)
          cv2.putText(img, "center", (cX - 20, cY - 20),
          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
      #Drawing a vertical central line(at x=170) with RED color(BGR)
          cv2.line(img,(320,0),(320,640),(0,0,255),2)
          cv2.line(img,(0,320),(640,320),(0,0,255),2)
      #Drawing a vertical line at the centre with Blue color
          cv2.line(img,(cX,0),(cX,640),(255,0,0),2)
          cv2.line(img,(0,cY),(640,cY),(255,0,0),2)
      #Displaying mask
          cv2.imshow("mask",mask)
      #Displaying image
          cv2.imshow("cam",img)
          error=(desired_posn-cX)
          integral=integral+(error*t)
          derivate=(error-previous_error)/t
          PID=(kp*error)+(ki*integral)+(kd*derivate)
          previous_error=error
          time.sleep(t)
          servo_signalx=(295+PID)
          a=int(float(servo_signalx))
          pwm.set_pwm(0, 0, a)
          error1=(desired_posn1-cY)
          integral1=integral1+(error1*t)
          derivate1=(error1-previous_error1)/t
          PID1=(kp*error1)+(ki*integral1)+(kd*derivate1)
          previous_error1=error1
          servo_signaly=(300+PID1)
          b=int(float(servo_signaly))
          pwm.set_pwm(15, 0, b)
          if a>550 and b>550:
             a=550
             b=550
          if a<200 and b<200:
             a=200
             b=200
     #press q to end loop
     if cv2.waitKey(1) & 0xFF == ord('q'):
       break