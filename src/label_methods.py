import crepe
from scipy.io import wavfile
from madmom.features.onsets import CNNOnsetProcessor
from madmom.features.beats import RNNBeatProcessor
from madmom.features.tempo import TempoEstimationProcessor
import numpy as np
import librosa
from crepe_notes.crepe_notes import run_crepe, process
from ablt.bass_line_transcriber import transcribe_single_bass_line
from ablt.signal_processing import lp_and_normalize
import os
from pathlib import Path
import torchaudio
import pesto
from basic_pitch.inference import predict


FS = 44100
MIDI_PITCH_MIN = 24
MIDI_PITCH_MAX = 60

PITCH_FREQUENCIES = np.around(440 * np.power(2, (np.arange(0, 128) - 69) / 12), 2)
SUB_BASS_FREQUENCIES = PITCH_FREQUENCIES[MIDI_PITCH_MIN : MIDI_PITCH_MAX + 1]
F_MIN = SUB_BASS_FREQUENCIES[0]
F_MAX = SUB_BASS_FREQUENCIES[-1]

T_MAX = 1 / F_MIN  # Longest Period

# pYIN parameters

FRAME_FACTOR = 2  # Number of periods that make an F0 estimation frame
FRAME_DUR = FRAME_FACTOR * T_MAX  # Duration of a frame in sec
FRAME_LEN = int(FRAME_DUR * FS)  # Frame Length


def baseline(audio_file):
    sr, audio = wavfile.read(audio_file)
    time, freq, confidence, activation = crepe.predict(
        audio, sr, step_size=10, model_capacity="tiny"
    )
    proc = CNNOnsetProcessor()

    onsets = proc(audio_file)
    output = []
    audio = audio.T.mean(axis=0)
    amp_envelope = np.abs(audio)
    scaled_amp_envelope = np.interp(
        amp_envelope, (amp_envelope.min(), amp_envelope.max()), (0, 127)
    )
    for i in range(len(onsets)):
        onset_strength = onsets[i]
        if onset_strength > 0.5:
            time = i / 100  # Madmom is 10ms per frame
            amplitude_at_onset = round(scaled_amp_envelope[int(time * sr)])
            pitch_at_onset = round(librosa.hz_to_midi(freq[int(i / 2)]))
            if amplitude_at_onset > 0:
                output.append((time, pitch_at_onset, amplitude_at_onset))
    return output


def araz(audio_file):
    proc = TempoEstimationProcessor(fps=100)
    act = RNNBeatProcessor()(audio_file)
    bpm = proc(act)[0][0]
    y, sr = librosa.load(audio_file, sr=44100)
    num_bars = np.floor(len(y) / (sr * 60 / bpm) / 4).astype(int)

    normalized_y = librosa.util.normalize(y)
    filtered_y = lp_and_normalize(normalized_y, 100, sr)

    output_dir = (
        Path("data") / "outputs" / audio_file.stem / "chorus" / "beat_positions"
    )
    output_audio_dir = (
        Path("data") / "outputs" / "filtered_audio" / "chorus" / "beat_positions"
    )

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_audio_dir, exist_ok=True)
    np.save(output_dir / f"{audio_file.stem}.npy", act)
    np.save(output_audio_dir / "filtered_audio.npy", filtered_y)
    transcribe_single_bass_line(
        str(output_audio_dir / "filtered_audio.npy"), BPM=bpm, N_bars=num_bars
    )


def crepe_notes(audio_file):
    step_size = 0.01
    frequency, confidence = run_crepe(audio_file, step_size * 1000)
    # Enforce frequency range
    frequency = np.clip(frequency, F_MIN, F_MAX)
    timed_output_notes, _ = process(frequency, confidence, audio_file, step_size=step_size, min_duration=0.07, min_velocity=15)
    output = []
    for note in timed_output_notes:
        output.append((note["start"], round(note["pitch"]), round(note["velocity"])))
    return output


def pesto_notes(audio_file):
    x, sr = torchaudio.load(audio_file)
    x = x.mean(dim=0)
    step_size = 0.01

    timesteps, pitch, confidence, activations = pesto.predict(
        x, sr, step_size=step_size * 1000, num_chunks=10
    )
    pitch = pitch.cpu().numpy()
    confidence = confidence.cpu().numpy()
    pitch = np.clip(pitch, F_MIN, F_MAX)

    timed_output_notes, _ = process(pitch, confidence, audio_file, step_size=step_size, min_duration=0.07, min_velocity=15)
    output = []
    for note in timed_output_notes:
        output.append((note["start"], round(note["pitch"]), round(note["velocity"])))
    return output


def basic_pitch(audio_file):
    model_output, midi_data, note_events = predict(
        audio_file,
        minimum_note_length=30,
        minimum_frequency=F_MIN,
        maximum_frequency=F_MAX,
    )
    output = []
    previous_start = -1
    for note in note_events:
        start, end, pitch, amplitude, pitch_bends = note
        if start == previous_start:
            continue
        previous_start = start
        velocity = int(amplitude * 127)
        output.append((start, pitch, velocity))
    return output
