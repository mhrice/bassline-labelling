## Bass Line Labeling Framework
This is a demo project to evaluate various methods to transcribe and reproduce bass lines from audio recordings.
In this project, we evaluated using various methods to transcribe and reproduce bass lines from audio recordings. The methods are: "baseline", "crepe_notes", "pesto_notes", and "basic_pitch". See the attached report for more details.

# Installation
```bash
pip install -e .
```
Note that this repo only works with python==3.10

Download the example-files from [here](https://drive.google.com/drive/folders/14LBnNa6wePeOPSE6KjEw0Wzb3wQ3enco?usp=drive_link) and place them in a directory called 'example-files' in the root of the project.

# Usage
```bash
    python scripts/label_and_generate.py
```

This will use the "crepe_notes" method to label the bass lines in the 'example-files' directory and generate the corresponding csv, midi, and audio files in the 'outputs/crepe_notes' directory. It uses the FluidSynth library to generate the audio files, so you'll need to have that installed on your system (follow the instructions [here](https://github.com/bzamecnik/midi2audio)).

# Generating with the Filobass Dataset
The report evaluated the methods using the "FiloBass" dataset. Download the dataset from [here](https://zenodo.org/records/10069709) and place it in a directory called 'FiloBass' in the root of the project.
You'll then need to convert all of the audio files to wav (I used FFMPEG). Then modify the `label_and_generate` script (uncomment the commented-out lines)

```bash
    python scripts/label_and_generate.py
    python scripts/evaluate.py
```

This will evaluate the performance of the "baseline", "crepe_notes", "pesto_notes", and "basic_pitch" methods on the FiloBass dataset. The results will be printed to the console.


# Evaluation on FiloBass Dataset
