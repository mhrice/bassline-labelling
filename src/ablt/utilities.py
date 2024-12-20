#!/usr/bin/env python
# coding: utf-8

import os
import json
import time
import psutil
import traceback

import numpy as np


#-------------------------------------------------- METADATA ------------------------------------------------------------

def read_track_dicts(path):
    with open(path, 'r') as infile:
        track_dicts = json.load(infile)
    return track_dicts 

#-------------------------------------------------- Beat, frequency ------------------------------------------------------------

def create_frequency_bins(fs, n_fft): 
    bin_width = (fs/2) / n_fft
    frequency_bins = np.arange(0, int((n_fft/2)+1))*bin_width
    return frequency_bins, bin_width

def get_chorus_beat_positions(output_dir):
    """
    Loads the beat positions of the progression.
    """
    title = os.path.basename(output_dir)
    return np.load(os.path.join(output_dir, 'chorus', 'beat_positions', title+'.npy'))
    
def get_bar_positions(beat_positions):
    """
   Finds the bar positions from a gşven beat positions array.     
    """    
    return np.array([val for idx,val in enumerate(beat_positions) if not idx%4])

def get_quarter_beat_positions(beat_positions):
    quarter_beats = []
    for i in range(len(beat_positions)-1):
        for qb in np.linspace(beat_positions[i],beat_positions[i+1], 4, endpoint=False):
            quarter_beats.append(qb)
            
    return np.array(quarter_beats)

def get_eighth_beat_positions(beat_positions):
    eighth_beats = []
    for i in range(len(beat_positions)-1):
        for qb in np.linspace(beat_positions[i],beat_positions[i+1], 8, endpoint=False):
            eighth_beats.append(qb)
            
    return eighth_beats

# Load Source Separation Model

def load_source_separation_model():
    separator = load_pretrained('demucs_extra')
    return separator

#-------------------------------------------------- Miscallenous ------------------------------------------------------------

def sample_and_hold(samples, N_samples):
    """
    Repeats each sample N_samples times correspondingly.
    """
    
    if isinstance(N_samples, int): # uniform sample rate
        return [f for f in samples for _ in range(N_samples)]
    
    else: # varying sample length 
        return [sample for idx, val in enumerate(N_samples) for sample in sample_and_hold([samples[idx]], val)] 

def export_function(array, directory, title):
    os.makedirs(directory, exist_ok=True)
    export_path = os.path.join(directory, '{}.npy'.format(title))
    np.save(export_path, array)

def batch_export_function(batch_dict, path):
    for title, array in batch_dict.items():
        export_function(array, path, title)

def exception_logger(dir, ex, title):
    date = time.strftime("%m-%d_%H-%M-%S")
    os.makedirs(dir, exist_ok=True)
    exception_str = ''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))
    exception_dir = os.path.join(dir, '{}_{}.txt'.format(date, type(ex).__name__))
    with open(exception_dir, 'a') as outfile:
        outfile.write(title+'\n'+exception_str+'\n'+'--'*40+'\n')

#-------------------------------------------------- Printing ------------------------------------------------------------

def print_midi_array(midi_array):  
    x = list([list(row) for row in midi_array])
    x.insert(0,['Start Beat', 'MIDI Number', 'Velocity', 'Duration'])
    print('{:^59}\n'.format('Bassline MIDI Array'))
    print('{:^15}{:^16}{:^14}{:^14}'.format('Start Beat', 'MIDI Number', 'Velocity', 'Duration'))
    print('-'*59)
    for row in midi_array:      
        start, dur = row[0], row[3]
        m, vel = row[1].astype(int), row[2].astype(int)   
        print('|{:^13}|{:^15}|{:^13}|{:^13}|'.format(start, m, vel, dur))

def print_symbolic_representation(symbolic_representation):
    print('{:^66}\n'.format('Bassline Symbolic Representation'))
    print(symbolic_representation[np.arange(0, len(symbolic_representation)).reshape(4,-1)])
    print('\nRepresentation Vector Length: {} (= 4 Bars = 16 Beats = 64 QuarterBeats)'.format(len(symbolic_representation)))   

def print_structured_representation(representation, M, SIL=1, SUS=26):
    print('SIL: {}, SUS:{}'.format(SIL, SUS))    
    bars = representation[np.arange(0, len(representation)).reshape(4,-1)]
    
    for i, bar in enumerate(bars):
        print('\n{:>21}'.format('Bar {}'.format(i)))
        beats = bar.reshape(4,-1)  
        
        for j, beat in enumerate(beats):
            
            if M == 8:
                string = 'Beat {:9<}: {}'.format(j, beat) # i*4+
                if j != 3:
                    string += '\n'
                print(string)                   
            if M == 4:
                print('Beat {:9<}:'.format(i*4+j))                
                qbeats = beat.reshape(4,-1)
                
                for k, qbeat in enumerate(qbeats):
                    string = 'Q-B {:9<}: {}'.format(k, qbeat)
                    if k==3:
                        string += '\n'
                    print(string)

def print_beat_matrix(representation, M, SIL=1, SUS=26, N_bars=4):    
    representation = representation.reshape((N_bars,4, 4*(8//M)))       
    ppb = 32//M # points per beat, 32 comes from the pYIN frame size
    tab = 2*ppb + (ppb-1)+ 2 # pretty print
    print('SIL: {}, SUS: {}'.format(SIL, SUS))
    for i in range(N_bars//2):
        print('\n{:>8}{:<{}}  {:<{}}'.format(' ','Bar {}'.format(2*i), tab+2, 'Bar {}'.format(2*i+1), tab))
        for j in range(4):
            print('Beat {}: {}   {}'.format(j, representation[2*i,j,:], representation[2*i+1,j,:]))

def print_transposed_beat_matrix(representation, M, SIL=1, SUS=26, N_bars=4):
    representation = representation.reshape((N_bars,4, 4*(8//M)))       
    ppb = 32//M # points per beat, 32 comes from the pYIN frame size
    tab = 2*ppb + (ppb-1)+ 2 # pretty print
    print('SIL: {}, SUS: {}'.format(SIL, SUS))
    for i in range(N_bars//2):
        print('\n{:>7}{:<{}}  {:<{}}'.format(' ','Beat {}'.format(2*i), tab+2, 'Beat {}'.format(2*i+1), tab))
        for j in range(4):
            print('Bar {}: {}   {}'.format(j, representation[j,2*i,:], representation[j,2*i+1,:]))

def print_monitoring():

    # Get cpu statistics
    cpu = str(psutil.cpu_percent()) + '%'

    # Calculate memory information
    memory = psutil.virtual_memory()
    # Convert Bytes to MB (Bytes -> KB -> MB)
    available = round(memory.available/1024.0/1024.0,1)
    total = round(memory.total/1024.0/1024.0,1)
    mem_info = str(available) + 'MB free / ' + str(total) + 'MB total ( ' + str(memory.percent) + '% )'

    # Calculate disk information
    disk = psutil.disk_usage('/')
    # Convert Bytes to GB (Bytes -> KB -> MB -> GB)
    free = round(disk.free/1024.0/1024.0/1024.0,1)
    total = round(disk.total/1024.0/1024.0/1024.0,1)
    disk_info = str(free) + 'GB free / ' + str(total) + 'GB total ( ' + str(disk.percent) + '% )'

    print("CPU Info --> ", cpu)
    print("Memory Info -->", mem_info)
    print("Disk Info -->", disk_info)