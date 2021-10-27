'''
Copyright (c) 2020 Pantelis Liolios
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from tkinter import Tk, filedialog, messagebox, simpledialog
from matplotlib.widgets import Cursor
from matplotlib.backend_bases import cursors
import matplotlib.backends.backend_tkagg as tkagg
import matplotlib
import tkinter
import cv2
import os
matplotlib.use('TkAgg')

from numpy import asarray, savetxt

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

coords = None
frame = None


def grab_frame(cap):
    ret, frame = cap.read()
    return cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)


def run():
    '''
    Main function of curve digitizer
    '''

    pixelCoord = None
    global frame, coords
    # open the dialog box
    # first hide the root window
    root = Tk()
    root.withdraw()
    root.config(cursor="tcross")

    cam = cv2.VideoCapture(0)  # camera index (default = 0) (added based on Randyr's comment).

    print('cam has image : %s' % cam.read()[0])  # True = got image captured.
    # False = no pics for you to shoot at.

    # Lets check start/open your cam!
    if cam.read() == False:
        cam.open()

    if not cam.isOpened():
        print('Cannot open camera')
    else:
        while True:
            ret, frame = cam.read()
            if coords != None:
                windSize = cv2.getWindowImageRect('webcam')
                window_name = frame
                start_point1 = (0, coords[1])
                end_point1 = (windSize[2], coords[1])
                start_point2 = (coords[0], 0)
                end_point2 = (coords[0], windSize[3])
                color = (250, 250, 250)
                thick = 1
                cross1 = cv2.line(window_name, start_point1, end_point1, color, thick)
                cross2 = cv2.line(window_name, start_point2, end_point2, color, thick)
                cv2.imshow('webcam', cross1)
                cv2.imshow('webcam', cross2)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(cross1, str(coords[0]) + ', ' +
                            str(coords[1]), (coords[0] + 10, coords[1] - 20), font,
                            1, (250, 250, 250), 1)
                cv2.imshow('webcam', cross1)
            else:
                cv2.imshow('webcam', frame)
            cv2.setMouseCallback('webcam', streamClicker)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()

def streamClicker(event, x, y, flags, param):
    global frame, coords
    # get the center reference point
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x, ' ', y)
        coords = (x, y)
        # display coordinates on stream window
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, str(x) + ', ' +
                    str(y), (x + 10, y - 20), font,
                    1, (255, 0, 0), 2)
        cv2.imshow('webcam', frame)
    if event == cv2.EVENT_MOUSEMOVE:
        windSize = cv2.getWindowImageRect('webcam')
        window_name = frame
        start_point1 = (0, y)
        end_point1 = (windSize[2], y)
        start_point2 = (x, 0)
        end_point2 = (x, windSize[3])
        color = (250 , 250, 250)
        thick = 1
        cross1 = cv2.line(window_name, start_point1, end_point1, color, thick)
        cross2 = cv2.line(window_name, start_point2, end_point2, color, thick)
        cv2.imshow('webcam', cross1)
        cv2.imshow('webcam', cross2)


if __name__ == "__main__":
    '''
    Digitize curves from scanned plots
    '''

    # run the main function
    run()