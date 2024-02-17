import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import csv
from scipy.io import wavfile
from scipy import signal
import pyaudio
from IPython.display import Audio

# Load the YAMNet model.
model = hub.load('https://tfhub.dev/google/yamnet/1')

# Find the name of the class with the top score when mean-aggregated across frames.
def class_names_from_csv(class_map_csv_text):
    """Returns a list of class names corresponding to the score vector."""
    class_names = []
    with tf.io.gfile.GFile(class_map_csv_text) as csvfile:
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
    print(f'{i+1}. {sound_event}')
