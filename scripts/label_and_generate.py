from pathlib import Path
from label_methods import (
    baseline,
    crepe_notes,
    pesto_notes,
    basic_pitch,
)
from generate import generate_midi
from tqdm import tqdm
from midi2audio import FluidSynth


def main():
    # audio_files = list((Path("FiloBass") / "audio_bass_stems").glob("*.wav"))
    audio_files = list((Path("example-files")).glob("*.wav"))

    print(f"Found {len(audio_files)} audio files")
    # methods = [baseline, crepe_notes, pesto_notes, basic_pitch]
    methods = [crepe_notes]



    for method in tqdm(methods):
        output_dir = Path("outputs") / method.__name__
        output_dir.mkdir(exist_ok=True, parents=True)
        for audio_file in tqdm(audio_files):
            p = audio_file
            labels = method(p)
            with open(output_dir / f"{p.stem}.csv", "w") as f:
                for label in labels:
                    f.write(",".join(map(str, label)) + "\n")
            generate_midi(
                output_dir / f"{p.stem}.csv", output_dir / f"{p.stem}_transcription.mid"
            )
            fs = FluidSynth()


            fs.midi_to_audio(
                output_dir / f"{p.stem}_transcription.mid",
                output_dir / f"{p.stem}_generated.wav",
            )


if __name__ == "__main__":
    main()
