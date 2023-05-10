# import the necessary packages
from imutils.video import VideoStream
import numpy as np
import argparse
import datetime
import imutils
import time
import cv2
import os
import re
import pygame
import smtplib
from gpiozero import MotionSensor


#Main def for running the system
def run_system():
    pygame.mixer.init()
    pygame.mixer.music.load('/home/nutmeg43/Downloads/alarm.mp3')

    pir0 = MotionSensor(4)
    pir1 = MotionSensor(17)
    pir2 = MotionSensor(27)
    pir3 = MotionSensor(22)
    pir4 = MotionSensor(12)
    pir5 = MotionSensor(16)
    pir6 = MotionSensor(20)
    pir7 = MotionSensor(18)
      
    pir_list = [pir0,pir1,pir2,pir3,pir4,pir5,pir6,pir7]
    sensor_cnts = [0,0,0,0,0,0,0,0]
    camera_efficiency = [3,3,3,3]
    wait_list = [0,0,0,0]

    #Make sure folders are empty
    empty_folders()
      
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the video file")
    ap.add_argument("-a", "--min-area", type=int, default=900, help="minimum area size")
    args = vars(ap.parse_args())

    # if the video argument is None, then we are reading from webcam
    if args.get("video", None) is None:
        vs1 = cv2.VideoCapture(0)
        vs2 = cv2.VideoCapture(2)
        vs3 = cv2.VideoCapture(3)
        vs4 = cv2.VideoCapture(4)
        time.sleep(2.0)
    # otherwise, we are reading from a video file
    else:
        vs1 = cv2.VideoCapture(args["video"])
        vs2 = cv2.VideoCapture(args["video"])
        vs3 = cv2.VideoCapture(args["video"])
        vs4 = cv2.VideoCapture(args["video"])

    # initialize the first frame in the videqo stream
    firstFrame1 = None
    firstFrame2 = None
    firstFrame3 = None
    firstFrame4 = None
    first_sample = 1
    motion_sensor_1 = 0
    frame_count = 0
    wait_cnt = 0
    sound_play = 0

    #Face detection
    face_cascade = cv2.CascadeClassifier('/home/nutmeg43/Projects/GIT/ECSE488_Project/face.xml')

    # loop over the frames of the video
    while True:
            
        #Get sensor information
        sensor_cnts = check_sensors(pir_list, sensor_cnts)

        #Motion near camera #1
        if(sensor_cnts[0] > 0 or sensor_cnts[1] > 0 or sensor_cnts[7] > 0):
            
            # grab the current frame and initialize the occupied/unoccupied
            ret1, frame1 = vs1.read()
            frame1 = frame1 if args.get("video", None) is None else frame1[1]
            text = "Unoccupied #1"
            
            if frame1 is None:
                break
            
            # resize the frames, convert it to grayscale, and blur it
            frame1 = imutils.resize(frame1, width=500)
            gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # if the first frame is None, initialize it
            if firstFrame1 is None:
                firstFrame1 = gray
                continue
            
            # compute the absolute difference between the current frame and
            # first frame
            frame1Delta = cv2.absdiff(firstFrame1, gray)        
            thresh1 = cv2.threshold(frame1Delta, 35, 255, cv2.THRESH_BINARY)[1]
            # dilate the thresholded image to fill in holes, then find contours
            # on thresholded image
            thresh1 = cv2.dilate(thresh1, None, iterations=2)
            cnts = cv2.findContours(thresh1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            
            # loop over the contours
            for c in cnts:
                #If small continue
                if cv2.contourArea(c) < args["min_area"]:
                    continue
                if(camera_efficiency[0] == 0) :
                    
                    #Reset camera delay
                    camera_efficiency[0] = 5
                    
                    #Check for a face
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    
                    #Draw the rectangle around each face
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame1, (x, y), (x+w, y+h), (255, 0, 0), 2)
                        
                        if len(faces) != 0:
                            if sound_play == 0:
                                pygame.mixer.music.play()
                                sound_play = 1
                else:
                    camera_efficiency[0] -= 1
                    
                text = "Occupied #1"
                      
            # draw the text and timestamp on the frame
            cv2.putText(frame1, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame1, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame1.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            
            # show the frame and record if the user presses a key
            cv2.imwrite("Frames1/frame1%d.jpg" % frame_count,frame1)
            wait_cnt = 15
            wait_list[0] = 15
            
        elif(wait_list[0] == 0 or first_sample == 1):
            #print("wait0")
            wait_list[0] = 15
            ret1, frame1 = vs1.read()
            frame1 = frame1 if args.get("video", None) is None else frame1[1]
            frame1 = imutils.resize(frame1, width=500)
            text = "Unoccupied #1"
            cv2.putText(frame1, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame1, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame1.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            # show the frame and record if the user presses a key
            cv2.imwrite("Frames1/frame1%d.jpg" % frame_count,frame1)

        
        
        #Motion near camera #2
        if(sensor_cnts[1] > 0 or sensor_cnts[2] > 0 or sensor_cnts[3] > 0):

            ret2, frame2 = vs2.read()
            frame2 = frame2 if args.get("video", None) is None else frame2[1]
            text = "Unoccupied #2"
            if frame2 is None:
                break            
           
            frame2 = imutils.resize(frame2, width=500)
            gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # if the first frame is None, initialize it
            if firstFrame2 is None:
                firstFrame2 = gray
                continue
            
            # compute the absolute difference between the current frame and
            # second frame
            text = "Unoccupied #2"
            frame2Delta = cv2.absdiff(firstFrame2, gray)
            thresh2 = cv2.threshold(frame2Delta, 35, 255, cv2.THRESH_BINARY)[1]
            # dilate the thresholded image to fill in holes, then find contours
            # on thresholded image
            thresh2 = cv2.dilate(thresh2, None, iterations=2)
            cnts = cv2.findContours(thresh2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            
            # loop over the contours
            for c in cnts:
                # if the contour is too small, ignore it
                
                if cv2.contourArea(c) < args["min_area"]:
                    continue
                    
                if(camera_efficiency[1] == 0) :
                    
                    #Reset camera delay
                    camera_efficiency[1] = 5
                    
                    #Check for a face
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    
                    #Draw the rectangle around each face
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame2, (x, y), (x+w, y+h), (255, 0, 0), 2)
                        
                        if len(faces) != 0:
                            if sound_play == 0:
                                pygame.mixer.music.play()
                                sound_play = 1
                else:
                    camera_efficiency[1] -= 1
                    
                text = "Occupied #2"        
            
            # draw the text and timestamp on the frame
            cv2.putText(frame2, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame2, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame2.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            
            # show the frame and record if the user presses a key
            cv2.imwrite("Frames2/frame2%d.jpg" % frame_count,frame2)
            wait_cnt = 15
            wait_list[1] = 15
            
        elif(wait_list[1] == 0 or first_sample == 1):
            #print("wait1")
            wait_list[1] = 15
            ret2, frame2 = vs2.read()
            frame2 = frame2 if args.get("video", None) is None else frame2[1]
            frame2 = imutils.resize(frame2, width=500)
            text = "Unoccupied #2"
            cv2.putText(frame2, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame2, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame2.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            # show the frame and record if the user presses a key
            cv2.imwrite("Frames2/frame2%d.jpg" % frame_count,frame2)
          
                
        #Motion near camera #3
        if(sensor_cnts[3] > 0 or sensor_cnts[4] > 0 or sensor_cnts[5] > 0):
            
            ret3, frame3 = vs3.read()
            frame3 = frame3 if args.get("video", None) is None else frame3[1]
            text = "Unoccupied #3"
            if frame3 is None:
                break            
           
            frame3 = imutils.resize(frame3, width=500)
            gray = cv2.cvtColor(frame3, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # if the first frame is None, initialize it
            if firstFrame3 is None:
                firstFrame3 = gray
                continue
            
            # compute the absolute difference between the current frame and
            # second frame
            text = "Unoccupied #3"
            frame3Delta = cv2.absdiff(firstFrame3, gray)
            thresh3 = cv2.threshold(frame3Delta, 35, 255, cv2.THRESH_BINARY)[1]
            # dilate the thresholded image to fill in holes, then find contours
            # on thresholded image
            thresh3 = cv2.dilate(thresh3, None, iterations=2)
            cnts = cv2.findContours(thresh3.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            
            
            # loop over the contours
            for c in cnts:
                # if the contour is too small, ignore it
                
                if cv2.contourArea(c) < args["min_area"]:
                    continue
                    
                if(camera_efficiency[1] == 0) :
                    
                    #Reset camera delay
                    camera_efficiency[1] = 5
                    
                    #Check for a face
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    
                    #Draw the rectangle around each face
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame3, (x, y), (x+w, y+h), (255, 0, 0), 2)
                        
                        if len(faces) != 0:
                            if sound_play == 0:
                                pygame.mixer.music.play()
                                sound_play = 1
                else:
                    camera_efficiency[1] -= 1
                    
                text = "Occupied #3"        
            
            # draw the text and timestamp on the frame
            cv2.putText(frame3, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame3, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame3.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            
            # show the frame and record if the user presses a key
            cv2.imwrite("Frames3/frame3%d.jpg" % frame_count,frame3)
            wait_cnt = 15
            wait_list[1] = 15
            
        elif(wait_list[1] == 0 or first_sample == 1):
            #print("wait1")
            wait_list[1] = 15
            ret3, frame3 = vs3.read()
            frame3 = frame3 if args.get("video", None) is None else frame3[1]
            frame3 = imutils.resize(frame3, width=500)
            text = "Unoccupied #3"
            cv2.putText(frame3, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame3, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame3.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            # show the frame and record if the user presses a key
            cv2.imwrite("Frames3/frame3%d.jpg" % frame_count,frame3)
          
          
        #Motion near camera #4
        if(sensor_cnts[5] > 0 or sensor_cnts[6] > 0 or sensor_cnts[7] > 0):
            
            ret4, frame4 = vs4.read()
            frame4 = frame4 if args.get("video", None) is None else frame4[1]
            text = "Unoccupied #4"
            if frame4 is None:
                break            
           
            frame4 = imutils.resize(frame4, width=500)
            gray = cv2.cvtColor(frame4, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # if the first frame is None, initialize it
            if firstFrame4 is None:
                firstFrame4 = gray
                continue
            
            # compute the absolute difference between the current frame and
            # second frame
            text = "Unoccupied #4"
            frame4Delta = cv2.absdiff(firstFrame4, gray)
            thresh4 = cv2.threshold(frame4Delta, 35, 255, cv2.THRESH_BINARY)[1]
            # dilate the thresholded image to fill in holes, then find contours
            # on thresholded image
            thresh4 = cv2.dilate(thresh4, None, iterations=2)
            cnts = cv2.findContours(thresh4.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            
            
            # loop over the contours
            for c in cnts:
                # if the contour is too small, ignore it
                
                if cv2.contourArea(c) < args["min_area"]:
                    continue
                    
                if(camera_efficiency[1] == 0) :
                    
                    #Reset camera delay
                    camera_efficiency[1] = 5
                    
                    #Check for a face
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    
                    #Draw the rectangle around each face
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame4, (x, y), (x+w, y+h), (255, 0, 0), 2)
                        
                        if len(faces) != 0:
                            if sound_play == 0:
                                pygame.mixer.music.play()
                                sound_play = 1
                else:
                    camera_efficiency[1] -= 1
                    
                text = "Occupied #4"        
            
            # draw the text and timestamp on the frame
            cv2.putText(frame4, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame4, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame4.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            
            # show the frame and record if the user presses a key
            cv2.imwrite("Frames4/frame4%d.jpg" % frame_count,frame4)
            wait_cnt = 15
            wait_list[1] = 15
            
        elif(wait_list[1] == 0 or first_sample == 1):
            #print("wait1")
            wait_list[1] = 15
            ret4, frame4 = vs4.read()
            frame4 = frame4 if args.get("video", None) is None else frame4[1]
            frame4 = imutils.resize(frame4, width=500)
            text = "Unoccupied #4"
            cv2.putText(frame4, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame4, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame4.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            # show the frame and record if the user presses a key
            cv2.imwrite("Frames4/frame4%d.jpg" % frame_count,frame4)
              
          
        #For case where there has been no motion for while for all frames, sample camera slowly  
        if(wait_cnt <= 0):
            wait_cnt = 15
            
            #Stop the alarm
            pygame.mixer.music.stop()
            sound_play = 0 
            
            #Combine frames
            Hori = np.concatenate((frame1, frame2, frame3,frame4), axis=1)
            cv2.imshow('Video Feed', Hori)
        
        #Case where there was motion recently, therefore use information from those samples
        else:        
            #Concat images and display
            Hori = np.concatenate((frame1, frame2, frame3,frame4), axis=1)
            cv2.imshow('Video Feed', Hori)
            frame_count = frame_count + 1 
            
        #Decrement wait counters
        wait_cnt -= 1
        wait_list[0] -= 1
        wait_list[1] -= 1
        wait_list[2] -= 1
        wait_list[3] -= 1
        
        key = cv2.waitKey(1) & 0xFF
            
        # if the `q` key is pressed, break from the lop
        if key == ord("q"):
            break
                
    # cleanup the camera and close any open windows
    vs1.release()
    vs2.release()
    cv2.destroyAllWindows()
    make_video()


#Def to check the sensors and return list of sensors that are activated
def check_sensors(pir_list, sensor_cnts):
       
    for i in range(len(pir_list)):

        if pir_list[i].motion_detected:
            print(i)
            sensor_cnts[i] = 15
            time.sleep(.001)
        else:
            #print(pir_list[i])
            sensor_cnts[i] -= 1 
            time.sleep(.001)

    return sensor_cnts


#Empties folders
def empty_folders():
    #Empty folder before runnings, make this def too probably
    dir = 'Frames1'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir,f))
        
    #Empty folder before runnings, make this def too probably
    dir = 'Frames2'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir,f))
    
    #Empty folder before runnings, make this def too probably
    dir = 'Frames3'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir,f))
    
    #Empty folder before runnings, make this def too probably
    dir = 'Frames4'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir,f))
    
#Def to make a video from each of the cameras
def make_video():
    
    ##CREATE VIDEO
    image_folder = 'Frames1'
    video_name = 'video_cam_1.avi'
    fps = 5

    images = [img for img in os.listdir(image_folder)]
    images.sort(key=lambda f: int(re.sub('\D', '', f)))

    frame = cv2.imread(os.path.join(image_folder,images[0]))
    height,width,layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, 10, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder,image)))

    cv2.destroyAllWindows()
    video.release()


    ##CREATE VIDEO
    image_folder = 'Frames2'
    video_name = 'video_cam_2.avi'
    fps = 5

    images = [img for img in os.listdir(image_folder)]
    images.sort(key=lambda f: int(re.sub('\D', '', f)))

    frame = cv2.imread(os.path.join(image_folder,images[0]))
    height,width,layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, 10, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder,image)))

    cv2.destroyAllWindows()
    video.release()
    
    ##CREATE VIDEO
    image_folder = 'Frames3'
    video_name = 'video_cam_3.avi'
    fps = 5

    images = [img for img in os.listdir(image_folder)]
    images.sort(key=lambda f: int(re.sub('\D', '', f)))

    frame = cv2.imread(os.path.join(image_folder,images[0]))
    height,width,layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, 10, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder,image)))

    cv2.destroyAllWindows()
    video.release()
    
    
    ##CREATE VIDEO
    image_folder = 'Frames4'
    video_name = 'video_cam_4.avi'
    fps = 5

    images = [img for img in os.listdir(image_folder)]
    images.sort(key=lambda f: int(re.sub('\D', '', f)))

    frame = cv2.imread(os.path.join(image_folder,images[0]))
    height,width,layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, 10, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder,image)))

    cv2.destroyAllWindows()
    video.release()
    
    #send_email_alert()


def send_email_alert():

    #These lines are for the email 
    user = "jbs176@case.edu" # replace with your CWRU email address
    pwd = "I Lov3 Natal13 So Much" # replace with your CWRU password
    recipient = "jsalmon4302@gmail.com" # replace with the recipient's email address

    subject = 'Intruder Alert Email' 
    text = 'An intruder has been detected in the warehouse facility' 

    email_text = """\
    From: %s
    To: %s
    Subject: %s
    %s
    """ % (user, recipient, subject, text)

    try:
        # Email server
        emserver = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        emserver.ehlo()

        #Logging in
        emserver.login(user, pwd)

        #Sending email
        emserver.sendmail(user, recipient, email_text)
        emserver.close()
        print("Email Sent")
    except Exception as e:
        print("Email wasn't sent due to:", e)

if __name__ == '__main__':
    run_system()