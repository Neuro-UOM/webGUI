#!/usr/bin/env python
import time
from emokit.emotiv import Emotiv

from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
import glob
import pandas as pd
from scipy import signal

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

    # extracted from : https://stackoverflow.com/questions/39032325/python-high-pass-filter
def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def Fourier_Thread(O2_array):
    # specifying the O2 node for the value
    y = O2_array
    y = butter_highpass_filter(y,5,132,5)

    ps = np.abs(np.fft.fft(y))**2

    time_step = float(1)/128
    freqs = np.fft.fftfreq( y.size , time_step )
    idx = np.argsort(freqs)
    
    socketio.emit('fourier_response',{'data': 'Server generated event', 'freq': freqs.tolist() , 'ps':ps.tolist() , 'idx':idx.tolist() }, namespace='/test')

    # return freqs[idx] , ps[idx]

def PSDA_Thread(O2_array):
    # specifying the O2 node for the value
    # power spectral density analysis
    y = O2_array
    y = butter_highpass_filter(y,5,132,5)
    time_step = float(1)/128
    
    f, psd = signal.periodogram(y, time_step)
    # f frequency , psd power spectral density
    
    socketio.emit('fourier_response',{'data': 'Server generated event', 'freq': freqs.tolist() , 'ps':ps.tolist() , 'idx':idx.tolist() }, namespace='/test')

    # return freqs[idx] , ps[idx]



def collect_raw_thread():

    """ collect raw data from another thread"""

    sensor_names = ["T7","T8","P7","P8","O1","O2"]

    with Emotiv(display_output=True, write=True, write_decrypted=True, verbose=True, output_path= "data") as headset:
        O2_array = []
        while True:
            packet = headset.dequeue()
            sensor_vals = []
            if packet is not None:
                for i in sensor_names:
                    sensor_vals.append(dict(packet.sensors)[i]['value'])
                
                O2_array.append(sensor_vals[5])
                
                socketio.sleep(0.0078)

                if len(O2_array)%1024 == 0:
                    Fourier_Thread(O2_array[-1024:])
                    
                arr = sensor_vals
                
                socketio.emit('array_response',{'data': 'Server generated event', 'data': O2_array }, namespace='/test')
                socketio.emit('raw_response',{'data': 'Server generated event', 'raw_array': arr}, namespace='/test')


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(0.01)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room', namespace='/test')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace='/test')
def rawData():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=collect_raw_thread)
    emit('raw_response', {'data': 'Connected', 'raw_array': [1,1,1,1,1,1]})
# def test_connect():
#     global thread
#     if thread is None:
#         thread = socketio.start_background_task(target=background_thread)
#     emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
