import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore"); 
    import matplotlib.pyplot as plt

import sys
import signal
import threading
import time
import logging
import math
import collections
import numpy as np
import struct
import json

import socket
import errno

# IP_ADDRESS = "192.168.1.53"
IP_ADDRESS = "192.168.43.51"

TCP_PORT_NUMBER = 5002
UDP_PORT_NUMBER = 8080

CHUNK    = 512
BYTES    = 2 * CHUNK
BYTES = 110

is_finished = False

def signal_handler(signal, frame):
    global is_finished
    print "You pressed CTRL + C!"
    is_finished = True

# Main function
def main():
    global is_finished

    # Get logger class
    log = logging.getLogger("Main")

    # Create signal handler event
    signal.signal(signal.SIGINT, signal_handler)

    print "Press CTRL+C to stop!"

    # Open UDP socket and bind it
    print "Open UDP server socket"
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((IP_ADDRESS, UDP_PORT_NUMBER))
    udp_sock.settimeout(0.1)

    # Prepare figure to draw plots
    fig = plt.figure(figsize=(12, 9))

    plt.ion()
    fig.show(False)

    # Two subplots, unpack the axes array immediately
    ax2 = fig.add_subplot(2,1,1)
    ax3 = fig.add_subplot(2,1,2)

    fig.show()
    fig.canvas.draw()

    # start data collection
    ydata_temp = []
    ydata_light = []
    ydata_accel_x = []
    ydata_accel_y = []
    ydata_accel_z = []
    
    maxLength = 50

    # Wait until audio playback is complete
    while (not is_finished):
        try:
            # Get data from UDP socket
            data, addr = udp_sock.recvfrom(BYTES)

            # "{\"id\": \"%d\", \"temperature\": \"%.3f\", \"light\": \"%.3f\", \"accel_x\": \"%d\", \"accel_y\": \"%d\", \"accel_z\": \"%d\"}",

            json_obj = json.loads(data)
            temp = json_obj.get('temperature')
            light = json_obj.get('light')
            accel_x = json_obj.get('accel_x')
            accel_y = json_obj.get('accel_y')
            accel_z = json_obj.get('accel_z')

            ydata_temp.append(temp)
            ydata_light.append(light)
            ydata_accel_x.append(accel_x)
            ydata_accel_y.append(accel_y)
            ydata_accel_z.append(accel_z)
            
            length = len(ydata_temp)
            if length >= maxLength:
                del ydata_temp[0]
                del ydata_light[0]
                del ydata_accel_x[0]
                del ydata_accel_y[0]
                del ydata_accel_z[0]

            ax2.clear()
            ax2.set_title("Medidas")
            ax2.set_ylabel("Temperatura")
            ax2.set_xlabel("Muestra")
            ax2.grid(True)
            # ax2.set_ylim([0,30])
            ax2.plot(ydata_light)

            ax3.clear()
            ax3.set_title("Medidas")
            ax3.set_ylabel("Luz")
            ax3.set_xlabel("Muestra")
            ax3.grid(True)
            # ax3.set_ylim([-10,10])
            # ax3.set_ylim([0,400])
            ax3.plot(ydata_accel_z)

            fig.canvas.draw()
            fig.canvas.flush_events()
##            plt.pause(0.0001)

        except:
            pass

    log.debug("Finishing...")

    # Close UDP socket
    print "Close UDP socket"
    udp_sock.close()
    plt.ioff()
    plt.close(fig)

# Execute main function
if __name__ == "__main__":
    main()
