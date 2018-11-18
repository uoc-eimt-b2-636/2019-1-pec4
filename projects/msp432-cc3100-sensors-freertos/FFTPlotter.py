# -*- coding: utf-8 -*-

import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore"); 
    import matplotlib.pyplot as plt

import sys
import threading
import collections
import struct
import logging
import time
import json

import numpy as np

class FFTPlotter(threading.Thread):
    def __init__(self, event = None):
        threading.Thread.__init__(self)

        self.event = event

        self.log = logging.getLogger("FFTPlotter")      

        self.time = collections.deque(maxlen = 100)
        self.temp = collections.deque(maxlen = 100)
        self.light = collections.deque(maxlen = 100)
        self.accel_x = collections.deque(maxlen = 100)
        self.accel_y = collections.deque(maxlen = 100)
        self.accel_z = collections.deque(maxlen = 100)

        self.counter = 0
        
        self.time.append(0.0)
        self.temp.append(0.0)
        self.light.append(0.0)
        self.accel_x.append(0.0)
        self.accel_y.append(0.0)
        self.accel_z.append(0.0)
        
        self.is_finished = False

    def exit(self):
        self.log.debug("Exitting")
        self.is_finished = True

    def run(self):
        self.log.debug("Starting")

        fig = plt.figure(figsize=(12, 9))

        plt.ion()
        fig.show(False)

        # Two subplots, unpack the axes array immediately
        ax1 = fig.add_subplot(3,1,1)
        ax2 = fig.add_subplot(3,1,2)
        ax3 = fig.add_subplot(3,1,3)
        fig.subplots_adjust(hspace=0.25)

        line1, = ax1.plot(self.time, self.temp, linewidth=2, color='r', label='Target value')
        line2, = ax2.plot(self.time, self.light, linewidth=2, color='b', label='Current value')
        line31, = ax3.plot(self.time, self.accel_x, linewidth=2, color='b', label='PWM value')
        line32, = ax3.plot(self.time, self.accel_y, linewidth=2, color='r', label='PWM value')
        line33, = ax3.plot(self.time, self.accel_z, linewidth=2, color='y', label='PWM value')

        ax1.set_title("Temperature")
        ax1.set_ylabel("degree Celsius")
        # ax1.set_xlabel("Sample #")
        ax1.grid(True)

        ax2.set_title("Light intensity")
        ax2.set_ylabel("Lux")
        # ax2.set_xlabel("Sample #")
        ax2.grid(True)

        ax3.set_title("Acceleration")
        ax3.set_ylabel("milliG")
        ax3.set_xlabel("Sample #")
        ax3.grid(True)

        fig.show()
        fig.canvas.draw()

        while not self.is_finished:
            # Wait for image to be received or timeout
            if (self.event.wait(0.01)):
                self.event.clear()

                if (self.counter>=50):
                    ax1.axis([self.counter-50, self.counter, min(self.temp)-10, max(self.temp)+10])
                    ax2.axis([self.counter-50, self.counter, min(self.light)-10, max(self.light)+10])
                    ax3.axis([self.counter-50, self.counter, -2000, 2000])
                else:
                    ax1.axis([0, self.counter, min(self.temp)-10, max(self.temp)+10])
                    ax2.axis([0, self.counter, min(self.light)-10, max(self.light)+10])
                    ax3.axis([0, self.counter, -2000, 2000])

                line1.set_data(self.time, self.temp)
                line2.set_data(self.time, self.light)
                line31.set_data(self.time, self.accel_x)
                line32.set_data(self.time, self.accel_y)
                line33.set_data(self.time, self.accel_z)

                fig.canvas.draw()

                fig.canvas.flush_events()

        plt.ioff()
        plt.close()

        self.log.debug("Exitted")
            
    
    def set_data(self, data):
        self.counter += 1
        json_obj = json.loads(data)
        try:
            temp = float(json_obj.get('temperature'))
            light = float(json_obj.get('light'))
            accel_x = float(json_obj.get('accel_x'))
            accel_y = float(json_obj.get('accel_y'))
            accel_z = float(json_obj.get('accel_z'))

            self.time.append(self.counter)
            self.temp.append(temp)
            self.light.append(light)
            self.accel_x.append(accel_x)
            self.accel_y.append(accel_y)
            self.accel_z.append(accel_z)
        except:
            pass
