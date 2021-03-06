# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:45:42 2018

@author: Caihao.Cui
"""
from __future__ import print_function
import pyzbar.pyzbar as pyzbar
import numpy as np
import cv2
import time
import json
import os
import web3
import time
import board
import neopixel
from web3.auto import w3
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

# get the webcam:
cap = cv2.VideoCapture(0)

cap.set(3,640)
cap.set(4,480)
#160.0 x 120.0
#176.0 x 144.0
#320.0 x 240.0
#352.0 x 288.0
#640.0 x 480.0
#1024.0 x 768.0
#1280.0 x 1024.0

# cap.set(cv2.CAP_PROP_FPS,30)
#time.sleep(2)

addresses = {}



## neopixel
# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 24

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False,
                           pixel_order=ORDER)

def decode(im) :
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)
    return decodedObjects


## NeoPixel Functions
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos*3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos*3)
        g = 0
        b = int(pos*3)
    else:
        pos -= 170
        r = 0
        g = int(pos*3)
        b = int(255 - pos*3)
    return (r, g, b) if ORDER == neopixel.RGB or ORDER == neopixel.GRB else (r, g, b, 0)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

def m_rainbow_cycle(wait, times):
    for _ in range(times):
        rainbow_cycle(wait)
    pixels.fill((0,0,0))
    pixels.show()


def scanning(wait, times):
    for _ in range(times):
        pixels.fill((0, 255, 0))
        pixels.show()
        time.sleep(wait)
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(wait)


def scanned(wait, times):
    for _ in range(times):
        pixels.fill((255, 75, 0))
        pixels.show()
        time.sleep(wait)
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(wait)

def circle(delay, to_color, from_color= (0,0,0)):
    n = num_pixels
    for i in range(num_pixels):
        for j in range(n):
            if j == n-1:
                pixels[j] = to_color
            elif j >0:
                pixels[j] = to_color
                pixels[j-1] = from_color
            else:
                pixels[j] = to_color
            pixels.show()
            time.sleep(delay)
        n = n-1
    time.sleep(.5)
    pixels.fill(from_color)
    pixels.show()

#Clear Lights
white = (0,0,0)
pixels.fill(white)
pixels.show()

#Start Camera Cycle
print("here")
while(cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # Our operations on the frame come here
    im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    print(cap.get(5))
    decodedObjects = decode(im)


    for decodedObject in decodedObjects:
        my_json = decodedObject.data.decode('utf8').replace("'", '"')
        data = json.loads(my_json)
        if data["id"] not in addresses.keys():
            m_rainbow_cycle(.005,1)
            print('Type : ', decodedObject.type)
            addresses[data["id"]] = time.time()
            circle(.01,(0,255,0))
            break
        elif data["id"] in addresses.keys() :
            if time.time() - addresses[data["id"]]  > 10:
                scanned(.25, 2)
                # Reset to White
                pixels.fill(white)
                pixels.show()
    # Display the resulting frame
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break
    elif key & 0xFF == ord('s'): # wait for 's' key to save
        cv2.imwrite('Capture.png', frame)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
