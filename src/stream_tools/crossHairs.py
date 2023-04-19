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
from image_processing import bit_depth_conversion as bdc

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

coordsA = None
coordsB = None
frameA = None
frameB = None
xypA = (0, 0)
xypB = (0, 0)


def grab_frame(cap):
    ret, frame = cap.read()
    return cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)


def run(stream):
    '''
    Main function of curve digitizer
    '''

    pixelCoord = None
    global frameA, frameB, coordsA, coordsB
    # open the dialog box
    # first hide the root window
    root = Tk()
    root.withdraw()
    root.config(cursor="tcross")

    # cam = stream  # camera index (default = 0) (added based on Randyr's comment).
    #
    # # print('cam has image : %s' % cam.read()[0])  # True = got image captured.
    # # False = no pics for you to shoot at.
    #
    # # Lets check start/open your cam!
    # if stream.read() == False:
    #     stream.open()
    #
    # if not stream.isOpened():
    #     print('Cannot open cameras')
    # else:
    #     print('Cameras open')
    continue_stream = True
    color = (255 * 256, 10 * 256, 0)
    if stream.test:
        stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix)
        a_as_16bit = cv2.imread(stream.current_frame_a)
        b_as_16bit = cv2.imread(stream.current_frame_b)
        frameA = a_as_16bit
        frameB = b_as_16bit
        cv2.imshow('camA', frameA)
        cv2.imshow('camB', frameB)
        cv2.setMouseCallback('camA', streamClickerA)
        cv2.setMouseCallback('camB', streamClickerB)
        while continue_stream:
            stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix)
            # stream.current_frame_a = cv2.cvtColor(stream.current_frame_a, cv2.COLOR_GRAY2BGR)
            # stream.current_frame_b = cv2.cvtColor(stream.current_frame_b, cv2.COLOR_GRAY2BGR)
            a_as_16bit = stream.current_frame_a
            b_as_16bit = stream.current_frame_b
            frameA = a_as_16bit
            frameB = b_as_16bit
            # set frame for cam A
            if coordsA != None:
                windSize = cv2.getWindowImageRect('camA')
                window_name = frameA
                start_point1 = (0, coordsA[1])
                end_point1 = (windSize[2], coordsA[1])
                start_point2 = (coordsA[0], 0)
                end_point2 = (coordsA[0], windSize[3])
                thick = 2
                cross1 = cv2.line(window_name, start_point1, end_point1, color, thick)
                cross2 = cv2.line(window_name, start_point2, end_point2, color, thick)
                cv2.imshow('camA', cross1)
                cv2.imshow('camA', cross2)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(cross1, str(coordsA[0]) + ', ' +
                            str(coordsA[1]), (coordsA[0] + 10, coordsA[1] - 20), font,
                            1, color, 1)
            # crosshairs for A
            windSize = cv2.getWindowImageRect('camA')
            window_name = frameA
            start_point1 = (0, xypA[1])
            end_point1 = (windSize[2], xypA[1])
            start_point2 = (xypA[0], 0)
            end_point2 = (xypA[0], windSize[3])
            thick = 1
            cv2.line(window_name, start_point1, end_point1, color, thick)
            cv2.line(window_name, start_point2, end_point2, color, thick)
            # show cam A
            cv2.imshow('camA', frameA)
            # set frame for cam B
            if coordsB != None:
                windSize = cv2.getWindowImageRect('camB')
                window_name = frameB
                start_point1 = (0, coordsB[1])
                end_point1 = (windSize[2], coordsB[1])
                start_point2 = (coordsB[0], 0)
                end_point2 = (coordsB[0], windSize[3])
                thick = 2
                cv2.line(window_name, start_point1, end_point1, color, thick)
                cv2.line(window_name, start_point2, end_point2, color, thick)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frameB, str(coordsB[0]) + ', ' +
                            str(coordsB[1]), (coordsB[0] + 10, coordsB[1] - 20), font,
                            1, color, 1)
            # crosshairs for B
            windSize = cv2.getWindowImageRect('camB')
            window_name = frameB
            start_point1 = (0, xypB[1])
            end_point1 = (windSize[2], xypB[1])
            start_point2 = (xypB[0], 0)
            end_point2 = (xypB[0], windSize[3])
            thick = 1
            cv2.line(window_name, start_point1, end_point1, color, thick)
            cv2.line(window_name, start_point2, end_point2, color, thick)
            # show cam B
            cv2.imshow('camB', frameB)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue_stream = stream.keep_streaming()
        cv2.destroyAllWindows()
        return coordsA, coordsB
    else:
        stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix)
        a_as_16bit = bdc.to_16_bit(stream.current_frame_a)
        b_as_16bit = bdc.to_16_bit(stream.current_frame_b)
        frameA = cv2.cvtColor(a_as_16bit, cv2.COLOR_GRAY2BGR)
        frameB = cv2.cvtColor(b_as_16bit, cv2.COLOR_GRAY2BGR)
        cv2.imshow('camA', frameA)
        cv2.imshow('camB', frameB)
        cv2.setMouseCallback('camA', streamClickerA)
        cv2.setMouseCallback('camB', streamClickerB)
        while continue_stream:
            stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix)
            # stream.current_frame_a = cv2.cvtColor(stream.current_frame_a, cv2.COLOR_GRAY2BGR)
            # stream.current_frame_b = cv2.cvtColor(stream.current_frame_b, cv2.COLOR_GRAY2BGR)
            a_as_16bit = bdc.to_16_bit(stream.current_frame_a)
            b_as_16bit = bdc.to_16_bit(stream.current_frame_b)
            frameA = cv2.cvtColor(a_as_16bit, cv2.COLOR_GRAY2BGR)
            frameB = cv2.cvtColor(b_as_16bit, cv2.COLOR_GRAY2BGR)
            # set frame for cam A
            if coordsA != None:
                windSize = cv2.getWindowImageRect('camA')
                window_name = frameA
                start_point1 = (0, coordsA[1])
                end_point1 = (windSize[2], coordsA[1])
                start_point2 = (coordsA[0], 0)
                end_point2 = (coordsA[0], windSize[3])
                thick = 2
                cross1 = cv2.line(window_name, start_point1, end_point1, color, thick)
                cross2 = cv2.line(window_name, start_point2, end_point2, color, thick)
                cv2.imshow('camA', cross1)
                cv2.imshow('camA', cross2)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(cross1, str(coordsA[0]) + ', ' +
                            str(coordsA[1]), (coordsA[0] + 10, coordsA[1] - 20), font,
                            1, color, 1)
            # crosshairs for A
            windSize = cv2.getWindowImageRect('camA')
            window_name = frameA
            start_point1 = (0, xypA[1])
            end_point1 = (windSize[2], xypA[1])
            start_point2 = (xypA[0], 0)
            end_point2 = (xypA[0], windSize[3])
            thick = 1
            cv2.line(window_name, start_point1, end_point1, color, thick)
            cv2.line(window_name, start_point2, end_point2, color, thick)
            # show cam A
            cv2.imshow('camA', frameA)
            # set frame for cam B
            if coordsB != None:
                windSize = cv2.getWindowImageRect('camB')
                window_name = frameB
                start_point1 = (0, coordsB[1])
                end_point1 = (windSize[2], coordsB[1])
                start_point2 = (coordsB[0], 0)
                end_point2 = (coordsB[0], windSize[3])
                thick = 2
                cv2.line(window_name, start_point1, end_point1, color, thick)
                cv2.line(window_name, start_point2, end_point2, color, thick)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frameB, str(coordsB[0]) + ', ' +
                            str(coordsB[1]), (coordsB[0] + 10, coordsB[1] - 20), font,
                            1, color, 1)
            # crosshairs for B
            windSize = cv2.getWindowImageRect('camB')
            window_name = frameB
            start_point1 = (0, xypB[1])
            end_point1 = (windSize[2], xypB[1])
            start_point2 = (xypB[0], 0)
            end_point2 = (xypB[0], windSize[3])
            thick = 1
            cv2.line(window_name, start_point1, end_point1, color, thick)
            cv2.line(window_name, start_point2, end_point2, color, thick)
            # show cam B
            cv2.imshow('camB', frameB)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue_stream = stream.keep_streaming()
        cv2.destroyAllWindows()
        return coordsA, coordsB

def streamClickerA(event, x, y, flags, param):
    global frameA, coordsA, xypA
    color = (255 * 256, 10 * 256, 0)
    # get the center reference point
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x, ' ', y)
        coordsA = (x, y)
        # display coordinates on stream window
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frameA, str(x) + ', ' +
                    str(y), (x + 10, y - 20), font,
                    1, color, 2)
        cv2.imshow('camA', frameA)
    if event == cv2.EVENT_MOUSEMOVE:
        xypA = (x, y)


def streamClickerB(event, x, y, flags, param):
    global frameB, coordsB, xypB
    color = (255 * 256, 10 * 256, 0)
    # get the center reference point
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x, ' ', y)
        coordsB = (x, y)
        # display coordinates on stream window
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frameB, str(x) + ', ' +
                    str(y), (x + 10, y - 20), font,
                    1, color, 2)
        cv2.imshow('camB', frameB)
    if event == cv2.EVENT_MOUSEMOVE:
        xypB = (x, y)


if __name__ == "__main__":
    '''
    Digitize curves from scanned plots
    '''

    # run the main function
    run()