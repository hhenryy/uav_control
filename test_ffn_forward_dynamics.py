#!/usr/bin/env python3


import tensorflow as tf
import os
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow import contrib
import argparse
import sys
import shelve
import h5py
from esl_timeseries_dataset import esl_timeseries_dataset
from terminaltables import AsciiTable
from tqdm import tnrange, trange
import datetime
import matplotlib.pyplot as plt



parser = argparse.ArgumentParser(\
        prog='Test the feedforward neural network for the forward dynamics of a drone',\
        description=''
        )


parser.add_argument('-model', default='', help='path to feedforward neural network')
parser.add_argument('-dataset', default='', help='path to dataset to test')


args = parser.parse_args()

path_to_model = str(vars(args)['model'])
dataset = str(vars(args)['dataset'])

dataset_readme = dataset + '_readme'

print('----------------------------------------------------------------')
print("TensorFlow version: {}".format(tf.__version__))
print("Eager execution: {}".format(tf.executing_eagerly()))
print('----------------------------------------------------------------')

data =[]

def getReadmePath(path):
    readme = ''
    if 'checkpoints' in path:
        dirs = path.split('/')
        pos = dirs.index('checkpoints')
        for i in range(0,pos+1):
            readme += dirs[i] + '/'

    else:
        dirs = path.split('/')
        # pos = dirs.index("nn_mdl")
        pos = len(dirs)
        for i in range(0,pos-1):
            readme += dirs[i] + '/'

    readme += 'readme'
    return readme


model_readme = getReadmePath(path_to_model)

print('----------------------------------------------------------------')
print('Fetching model info from: {}'.format(model_readme))
print('----------------------------------------------------------------')

with shelve.open(model_readme) as db:
    window_size = db['window_size']
    batchsize = db['batch_size']
    # num_samples = int(db['dataset_num_entries'])
    maxUdot = db['maxUdot']
    maxVdot = db['maxVdot']
    maxWdot = db['maxWdot']
    maxP = db['maxP']
    maxQ = db['maxQ']
    maxR = db['maxR']
    dronename = db['drone_name']

    for key,value in db.items():
        data.append([str(key),str(value)])

db.close()

table  = AsciiTable(data)
table.inner_row_border = True
print(table.table)



data=[]
print('----------------------------------------------------------------')
print('Fetching dataset info from: {}'.format(dataset_readme))
print('----------------------------------------------------------------')
with shelve.open(dataset_readme) as db:
    for key,value in db.items():
        data.append([str(key),str(value)])
db.close()
table  = AsciiTable(data)
table.inner_row_border = True
print(table.table)

# Importing saved model
model = tf.keras.models.load_model(path_to_model,compile=False)


# [q1,q2,q3,q4,U,V,W,T1,T2,T3,T4]
input_indices= [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# [P,Q,R,Udot,Vdot,Wdot]
output_indices = [11, 12, 13, 14, 15, 16]

test_dataset = esl_timeseries_dataset(dataset,window_size,1,batchsize,input_indices,
                output_indices,shuffle=False)


counter = 0
total_predictions = test_dataset.getTotalPredictions()
predictions = np.zeros((total_predictions,6))

for (x_test, y_test) in test_dataset:

    predict = model.predict(x_test)
    predictions[counter:counter+batchsize,:] = predict
    counter += batchsize


title_pitchrate = 'Pitch rate, $P$, of {}'.format(dronename)

plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rc('font', size=12)

plt.figure(1)
plt.plot(predictions[:,0],'-', mew=1, ms=8,mec='w')
plt.plot(test_dataset[11,:],'-', mew=1, ms=8,mec='w')
# plt.plot(lol.transpose(),'-', mew=1, ms=8,mec='w')
plt.grid()
plt.legend(['$\hat{P}$', '$P$'])
plt.title(title_pitchrate)
# plt.xticks(graph_ticks_spacing, graph_ticks_words )
plt.xlabel('Time - [s]')
plt.ylabel('Pitch Rate - [rad/s]')

plt.figure(2)
plt.plot(predictions[:,1],'-', mew=1, ms=8,mec='w')
plt.plot(test_dataset[12,:],'-', mew=1, ms=8,mec='w')
plt.grid()
# plt.xticks(graph_ticks_spacing, graph_ticks_words )
plt.xlabel('time - [s]')
plt.legend(['$\hat{\dot{Q}}$', '$\dot{Q}$'])
#
#
plt.figure(3)
plt.plot(predictions[:,2],'-', mew=1, ms=8,mec='w')
plt.plot(test_dataset[13,:],'-', mew=1, ms=8,mec='w')
plt.grid()
# plt.xticks(graph_ticks_spacing, graph_ticks_words )
plt.xlabel('time - [s]')
plt.legend(['$\hat{\dot{R}}$', '$\dot{R}$'])
#
#
plt.figure(4)
plt.plot(predictions[:,3],'-', mew=1, ms=8,mec='w')
plt.plot(test_dataset[14,:],'-', mew=1, ms=8,mec='w')
plt.title('Acceleration In X Directions')
plt.grid()
# plt.xticks(graph_ticks_spacing, graph_ticks_words )
plt.xlabel('Time - [s]')
plt.legend(['$\hat{\dot{U}}$', '$\dot{U}$'])
plt.ylabel('Acceleration - [m/s$^{2}$]')

plt.figure(5)
plt.plot(predictions[:,4],'-', mew=1, ms=8,mec='w')
plt.plot(test_dataset[15,:],'-', mew=1, ms=8,mec='w')
plt.grid()
# plt.xticks(graph_ticks_spacing, graph_ticks_words )
plt.xlabel('time - [s]')
plt.legend(['$\hat{\dot{V}}$', '$\dot{V}$'])

plt.figure(6)
plt.plot(predictions[:,5],'-', mew=1, ms=8,mec='w')
plt.plot(test_dataset[16,:],'-', mew=1, ms=8,mec='w')
plt.grid()
# plt.xticks(graph_ticks_spacing, graph_ticks_words )
plt.xlabel('time - [s]')
plt.legend(['$\hat{\dot{W}}$', '$\dot{W}$'])

plt.show()
