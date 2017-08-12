# -*- coding: utf-8 -*-
# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to the console. 


import time

from emokit.emotiv import Emotiv

sensor_names = ["T7","T8","P7","P8","O1","O2"]

if __name__ == "__main__":
    with Emotiv(display_output=True, write=True, write_decrypted=True, verbose=True, output_path= "data") as headset:
        while True:
            packet = headset.dequeue()
            sensor_vals = []
            if packet is not None:
                for i in sensor_names:
                    sensor_vals.append(dict(packet.sensors)[i]['value'])
                print sensor_vals
            
            
            
            time.sleep(0.001)


