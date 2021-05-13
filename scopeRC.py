#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 07:00:22 2020

@author: inox
"""
from pyaudio import paInt16, PyAudio
from struct import unpack
from pyqtgraph import GraphicsWindow, setConfigOptions, LegendItem, QtCore, QtGui
from numpy import fft, arange, split, argmax, floor
from scipy.signal import find_peaks as fpeaks

#Inicialización de ventana gráfica con los cuadros de visualización y el dicionario de trazas a graficar
win = GraphicsWindow(title="Analizador de Espectro")
win.setWindowTitle("Analizador de Espectro")
setConfigOptions(antialias=True, background='k')
scope = win.addPlot(title="Waveform", row = 1, col = 1)
span = win.addPlot(title="FFT", row = 2, col = 1)
traces = dict()
legend = LegendItem()  

#Actualización (o inicialización) de las trazas de los cuadros de visualización
def set_plotdata(name, data_x, data_y):
    if name in traces:
        traces[name].setData(data_x, data_y)
    else:
        if name == 'waveform':
            traces[name] = scope.plot(pen='w', width=4)
            scope.setYRange(-2**(bits-1), 2**(bits-1), padding=0)
            scope.setXRange(t[0], t[-1], padding=0.00)
        if name == 'spectrum':
            traces[name] = span.plot(pen='c', width=4)
            span.setYRange(0, 500, padding = 0)
            span.setXRange(F[0], 6e3, padding = 0)
        if name == 'peaks':
            traces[name] = span.plot(pen = None, symbol = 'x')
            legend.setParentItem(span.graphicsItem())
            legend.setFixedWidth(110)
            legend.autoAnchor((670,30),relative = True)

#Actualizción de la leyenda que actúa como frecuencímetro
def set_legend(values):
    legend.clear()
    for item in values :
        legend.addItem(traces['spectrum'], "f = " + str(floor(item))+" Hz")
                    
#Configuración de canal de entrada de audio
BUFF = 1024*3
FORMAT = paInt16
bits = 16;
bitFormat = 'h'
RATE = 44100
ts = 1/RATE

audio = PyAudio()
stream = audio.open(
    format = FORMAT,
    channels = 1,
    rate = RATE,
    input = True,
    output = False,
    frames_per_buffer = BUFF)

#Inicialización de vectores de tiempo y frecuencia
t = arange(0, ts*BUFF, ts)
F = fft.fftfreq(BUFF, ts)
F = split(F,2)[0]
Threshold = 50

#Funciones de identificación y ordenamiento de picos
def getPeak(data, treshold):
    index = argmax(data)
    return index if data[index] > treshold else False

def sort_by(list1, list2): 
    zipped_pairs = zip(list2.get('peak_heights'), list1) 
    z = [x for _, x in sorted(zipped_pairs, reverse=True)] 
    return z 

#Bucle de Ejecución
def update():
    #Adquisición
    data = stream.read(BUFF)
    data_int = unpack(str(BUFF)+bitFormat, data)
    #Procesamiento
    data_F = fft.fft(data_int)/(2**bits)
    data_F = abs(data_F[0:len(data_F)//2])    
    peaks, amp = fpeaks(data_F, height=Threshold)
    peaks = sort_by(peaks, amp)[0:4]
    #Visualización
    set_plotdata('waveform', t, data_int)
    set_plotdata("spectrum", F, data_F)
    set_plotdata("peaks", F[peaks], data_F[peaks])
    set_legend(F[peaks])

#Temporizador de actualización
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(25)

#Disparador
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()