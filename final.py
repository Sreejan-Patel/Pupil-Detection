import thingspeak
import base64 
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
import json
import time, sys
import RPi.GPIO as GPIO
import numpy as np
import cv2

redPin = 18   #Set to appropriate GPIO
greenPin = 22 #Should be set in the 
bluePin = 37  #GPIO.BOARD format

hz = 75

# KEY
key = 'sreehaachapra123' #16 char for AES128

#FIX IV
iv = 'jansarannathi123'.encode('utf-8') #16 char for AES128



GPIO.setmode(GPIO.BOARD)

GPIO.setup(18, GPIO.OUT)# set GPIO 17 as output for white led  
GPIO.setup(22, GPIO.OUT)# set GPIO 27 as output for red led  
GPIO.setup(37, GPIO.OUT)# set GPIO 22 as output for red led

GPIO.output(18, GPIO.HIGH)
GPIO.output(22, GPIO.HIGH)
GPIO.output(37, GPIO.HIGH)

red = GPIO.PWM(18, int(hz))    # create object red for PWM on port 1
green = GPIO.PWM(22, int(hz))      # create object green for PWM on port 2
blue = GPIO.PWM(37, int(hz))      # create object blue for PWM on port 22

channel_id = 1850502  # put here the ID of the channel you created before
write_key = 'U22K59XZQ3MDYUOT' # update the "WRITE KEY"
read_key = '3ZEF0QV0PHCA8TAC'


diameter_1 = []
diameter_2 = []
diameter_3 = []
diameter_4 = []
diameter_5 = []
diameter_list = {}

def pupilDiameter(color, duration):
    eye_cascade = cv2.CascadeClassifier('haarcascae_eye.xml')
    cap = cv2.VideoCapture(0)
    blink =False
    kernel = np.ones((5,5),np.uint8)
    global a
    font = cv2.FONT_HERSHEY_DUPLEX
    
    start_time = time.time()

    try:
        while 1:
            if(time.time() - start_time >= duration):
                return
            
            ret, img = cap.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            eyes = eye_cascade.detectMultiScale(gray,1.1,7)
            if (len(eyes)>0):
                a = "Eye Open"
                
                if (blink==True):
                    blink=False
                   
                cv2.putText(img,a,(10,30), font, 1,(0,0,255),2,cv2.LINE_AA)
                
                for (ex,ey,ew,eh) in eyes:
                    roi_gray2 = gray[ey:ey+eh, ex:ex+ew]
                    roi_color2 = img[ey:ey+eh, ex:ex+ew]
                    blur = cv2.GaussianBlur(roi_gray2,(5,5),10)
                    erosion = cv2.erode(blur,kernel,iterations = 2)
                    ret3,th3 = cv2.threshold(erosion,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
                    circles = cv2.HoughCircles(erosion,cv2.HOUGH_GRADIENT,4,200,param1=20,param2=150,minRadius=0,maxRadius=0)
                    try:
                        for i in circles[0,:]:
                            
                            if(i[2]>0 and i[2]<155):
                                cv2.circle(roi_color2,(int(i[0]),int(i[1])),int(i[2]),(0,0,255),1)
                                cv2.putText(img,"Pupil Pos:",(450,30), font, 1,(0,0,255),2,cv2.LINE_AA)
                                cv2.putText(img,"X "+str(int(i[0]))+" Y "+str(int(i[1])),(430,60), font, 1,(0,0,255),2,cv2.LINE_AA)
                                d = (int(i[2])*2.0)
                                dmm = 1/(25.4/d)
                                if(color == 1):
                                    diameter_1.append(dmm)
                                elif(color == 2):
                                    diameter_2.append(dmm)
                                elif(color == 3):
                                    diameter_3.append(dmm)
                                elif(color == 4):
                                    diameter_4.append(dmm)
                                elif(color == 5):
                                    diameter_5.append(dmm)
                                
                                
                                    
                                cv2.putText(img,str('{0:.2f}'.format(dmm))+"mm",(10,60), font, 1,(0,0,255),2,cv2.LINE_AA)
                                cv2.circle(roi_color2,(int(i[0]),int(i[1])),2,(0,0,255),3)
                    except Exception as e:
                        pass
                    
            else:
                if (blink==False):
                    blink=True
                    if blink==True:
                         cv2.putText(img,"Blink",(10,90), font, 1,(0,0,255),2,cv2.LINE_AA)
                a="Eye Close" 
                cv2.putText(img,a,(10,30), font, 1,(0,0,255),2,cv2.LINE_AA)
                
            cv2.imshow('img',img)
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break     
        cap.release()
        cv2.destroyAllWindows()
    except:
        print("Error")
        
def encrypt(data):
    data= pad(data.encode(),16)
    cipher = AES.new(key.encode('utf-8'),AES.MODE_CBC,iv)
    return base64.b64encode(cipher.encrypt(data))
        

def check_start(channel):
    str=channel.get_field_last(field=1)
    dic=json.loads(str)
    status=int(dic["field1"])
    return status

def get_values(channel,id):
    strr=channel.get_field_last(field=id)
    dic=json.loads(strr)
    field = "field"+str(id)
    Values=dic[field]
    value = json.loads(Values)
    return value

def redOn(intensity):
    red.start(100-int(intensity))
    
def greenOn(intensity):
    green.start(100-int(intensity))
    
def blueOn(intensity):
    blue.start(100-int(intensity))
    
def yellowOn(intensity):
    red.start(100-int(intensity))
    green.start(100-int(intensity))
    
def whiteOn(intensity):
    red.start(100-int(intensity))
    green.start(100-int(intensity))
    blue.start(100-int(intensity))
    
def Off():
    red.start(100)
    green.start(100)
    blue.start(100)

color_coding = { 1: redOn, 2: greenOn, 3: blueOn, 4: yellowOn, 5: whiteOn}


if __name__ == "__main__":
        write_channel = thingspeak.Channel(id=channel_id, api_key=write_key)
        read_channel = thingspeak.Channel(id=channel_id, api_key=read_key, fmt = 'json')
        
        while True:
            diameter_1 = []
            diameter_2 = []
            diameter_3 = []
            diameter_4 = []
            diameter_5 = []
            name = ''
            check = check_start(write_channel)
            if(check == 0):
                time.sleep(15)
                continue
            
            
            if(check == 1):
                values = get_values(read_channel,2)
                user = get_values(read_channel,3)
                name = user["name"]
                colors = values["color"]
                intensity = values["intensity"]
                iterations = values["iterations"]
                duration = values["duration"]
                
                for color in colors:
                    
                    for i in range(iterations):
                        color_coding[int(color)](intensity)
                        if(int(color) == 1):
                            pupilDiameter(int(color), duration)
                        elif(int(color) == 2):
                            pupilDiameter(int(color), duration)
                        elif(int(color) == 3):
                            pupilDiameter(int(color), duration)
                        elif(int(color) == 4):
                            pupilDiameter(int(color), duration)
                        elif(int(color) == 5):
                            pupilDiameter(int(color), duration)
                        Off()
                        time.sleep(5)
                    
                    time.sleep(10)
            
            diameter_dic_1 = {"red": diameter_1}
            diameter_dic_2 = {"green": diameter_2}
            diameter_dic_3 = {"blue": diameter_3}
            diameter_dic_4 = {"yellow": diameter_4}
            diameter_dic_5 = {"white": diameter_5}
            
                    
            encrypt_diameter_1 = encrypt(str(diameter_dic_1))
            encrypt_diameter_2 = encrypt(str(diameter_dic_2))
            encrypt_diameter_3 = encrypt(str(diameter_dic_3))
            encrypt_diameter_4 = encrypt(str(diameter_dic_4))
            encrypt_diameter_5 = encrypt(str(diameter_dic_5))
            
            
            response = write_channel.update({'field1':0, 'field2':name, 'field4':encrypt_diameter_1.decode("utf-8", "ignore"), 'field5':encrypt_diameter_2.decode("utf-8", "ignore"), 'field6':encrypt_diameter_3.decode("utf-8", "ignore"), 'field7':encrypt_diameter_4.decode("utf-8", "ignore"), 'field3':encrypt_diameter_5.decode("utf-8", "ignore")})
         
                    
                
                
