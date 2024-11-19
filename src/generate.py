import csv
import pretty_midi as pm

DURATION = 0.1


def generate_midi(csv_path, output_path):
    output_midi = pm.PrettyMIDI()
    instrument = pm.Instrument(
        program=pm.instrument_name_to_program("Electric Bass (finger)")
    )
    previous_start = 0
    with open(csv_path) as f:
        reader = csv.reader(f)
        for row in reader:
            start, pitch, velocity = row
            start = float(start)
            previous_start = start
            pitch = int(pitch)
            velocity = int(velocity)
            end = start + DURATION
            instrument.notes.append(
                pm.Note(start=start, end=end, pitch=pitch, velocity=velocity)
            )
    output_midi.instruments.append(instrument)
    output_midi.write(str(output_path))
