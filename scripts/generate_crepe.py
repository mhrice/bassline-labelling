from generate import generate_midi
from pathlib import Path
from midi2audio import FluidSynth
from tqdm import tqdm

input_dir = Path("outputs") / "crepe_notes"
output_dir = Path("outputs") / "crepe_notes_updated"
output_dir.mkdir(exist_ok=True, parents=True)
audio_files = list((Path("FiloBass") / "audio_bass_stems").glob("*.wav"))
for audio_file in tqdm(audio_files):
    generate_midi(
                    input_dir / f"{audio_file.stem}.csv", output_dir / f"{audio_file.stem}_transcription.mid"
                )
    fs = FluidSynth(
        "/Users/matthewrice/Desktop/SGM-v2.01-YamahaGrand-Guit-Bass-v2.7.sf2"
    )
    fs.midi_to_audio(
        output_dir / f"{audio_file.stem}_transcription.mid",
        output_dir / f"{audio_file.stem}_generated.wav",
    )