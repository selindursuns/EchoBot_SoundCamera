import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import csv
from scipy.io import wavfile
from scipy import signal
import pyaudio
import math
import random
from visualizationref import *

# Load the YAMNet model.
model = hub.load('https://tfhub.dev/google/yamnet/1')

# Find the name of the class with the top score when mean-aggregated across frames.
def class_names_from_csv(class_map_csv_text):
    """Returns a list of class names corresponding to the score vector."""
    class_names = []
    with open(class_map_csv_text) as csvfile:  # Change tf.io.gfile.GFile to open
        reader = csv.DictReader(csvfile)
        for row in reader:
            class_names.append(row['display_name'])
    return class_names

class_map_path = model.class_map_path().numpy()
class_names = class_names_from_csv(class_map_path)

def ensure_sample_rate(original_sample_rate, waveform, desired_sample_rate=16000):
    """Resample the waveform if required."""
    if original_sample_rate != desired_sample_rate:
        desired_length = int(round(float(len(waveform)) /
                                   original_sample_rate * desired_sample_rate))
        waveform = signal.resample(waveform, desired_length)
    return desired_sample_rate, waveform

# Record 10 seconds of audio from the microphone
def record_audio(duration=10):
    p = pyaudio.PyAudio()
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    sample_rate = 16000
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=sample_rate,
                    frames_per_buffer=chunk,
                    input=True)
    
    frames = []
    print("Recording...")
    for i in range(0, int(sample_rate * duration / chunk)):
        data = stream.read(chunk)
        frames.append(data)
    print("Finished recording.")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    audio_data = b''.join(frames)
    return sample_rate, np.frombuffer(audio_data, dtype=np.int16)

sample_rate, wav_data = record_audio()
sample_rate, wav_data = ensure_sample_rate(sample_rate, wav_data)

# Analyze the entire audio recording for multiple sound events
waveform = wav_data / np.iinfo(np.int16).max

# Run the YAMNet model and check the output for multiple sound events
scores, embeddings, spectrogram = model(waveform)

# Convert scores to a NumPy array and calculate the mean
scores_np = scores.numpy()
mean_scores = scores_np.mean(axis=0)

# Find the top N classes with the highest mean scores
top_n_indices = mean_scores.argsort()[::-1][:10]
top_n_classes = [class_names[i] for i in top_n_indices]

print("Detected sounds in the recording:")
for i, sound_event in enumerate(top_n_classes):
    print(f'{i + 1}. {sound_event}')

# Visualization code
visualization_result = {}
for sound in top_n_classes:
    visualization_result[sound] = get_sound_label(sound) + random.random()

def get_the_sequence(visualization_result):
    sequence = []
    sorted_keys = sorted(visualization_result, key=visualization_result.get, reverse=True)
    for key in sorted_keys:
        sequence.append(key)
    return sequence

def print_circle_in_sequence(visualization_result):
    sequence = get_the_sequence(visualization_result)
    for sound in sequence:
        circle_radius = round(visualization_result[sound] * 1)
        word = sound
        print_circle_with_word_inside(circle_radius, word, get_sound_label(sound), random.randint(0, 30))

# Function to print a circle with a word inside
def print_circle_with_word_inside(radius, word, symbol="|", indent=0):
    size = radius * 2
    width = size
    word_length = len(word)
    word_start_indx = (width - word_length) // 2

    center_x = width // 2
    center_y = radius

    for y in range(size):
        for _ in range(indent):
            print(" ", end='')
        for x in range(width):
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            
            if y == center_y:
                if x < word_start_indx or x > word_start_indx + word_length - 1:
                    print(" ", end='')
                else:
                    print(word, end='')
                    break
            elif distance < radius:
                print(symbol, end='')
            else:
                print(" ", end='')
        print()

print_circle_in_sequence(visualization_result)
