import mir_eval
from pathlib import Path
import pretty_midi as pm
import numpy as np
import pandas as pd
from tqdm import tqdm

def evaluate(midi_path='*.crepe_notes.mid',
             midi_replace_str='.crepe_notes.mid',
             midi_replace_with='.mid',
             midi_ref_root='*.mid',
             output_label='crepe_notes'):
    results = []

    merge_tracks = True

    paths = sorted(Path('./').rglob(midi_path))

    for path in tqdm(paths):
        # print(f"{output_label}: {path}")
        est_path = str(path)
        ref_path = str(Path(midi_ref_root) / path.name.replace(midi_replace_str, midi_replace_with))

        ref = pm.PrettyMIDI(ref_path)
        est = pm.PrettyMIDI(est_path)

        ref_times = np.array([[n.start, n.end]
                              for n in ref.instruments[0].notes])
        ref_pitches = np.array(
            [pm.note_number_to_hz(n.pitch) for n in ref.instruments[0].notes])

        if merge_tracks:
            est_times = np.array(
                [[n.start, n.end]
                 for inst_notes in map(lambda i: i.notes, est.instruments)
                 for n in inst_notes])
            est_pitches = np.array([
                pm.note_number_to_hz(n.pitch)
                for inst_notes in map(lambda i: i.notes, est.instruments)
                for n in inst_notes
            ])
        else:
            est_times = np.array([[n.start, n.end]
                                  for n in est.instruments[0].notes])
            est_pitches = np.array([
                pm.note_number_to_hz(n.pitch) for n in est.instruments[0].notes
            ])

        first_ref_note = np.min(ref_times)
        last_ref_note = np.max(ref_times)
        est_times_valid_idxs = np.unique(
            np.where((est_times > first_ref_note)
                     & (est_times < last_ref_note))[0])

        est_times = est_times[est_times_valid_idxs]
        est_pitches = est_pitches[est_times_valid_idxs]
        eval_result = mir_eval.transcription.evaluate(ref_times, ref_pitches,
                                                      est_times, est_pitches,
                                                      onset_tolerance=0.05)
        eval_result['file'] = str(path)
        results.append(eval_result)
    df = pd.DataFrame(results)
    df.to_pickle(f'{output_label}_eval.pkl')
    pd.set_option('display.max_colwidth', None)
    print(df.describe()[['Precision_no_offset', 'Recall_no_offset', 'F-measure_no_offset', 'Average_Overlap_Ratio_no_offset']])

# print('baseline')
# evaluate('outputs/baseline/*_transcription.mid',  '_transcription.mid', '.mid', "FiloBass/midi_fully_aligned", 'test')
# print('crepe_notes')
# evaluate('outputs/crepe_notes/*_transcription.mid',  '_transcription.mid', '.mid', "FiloBass/midi_fully_aligned", 'test')
# print('pesto_notes')
# evaluate('outputs/pesto_notes/*_transcription.mid',  '_transcription.mid', '.mid', "FiloBass/midi_fully_aligned", 'test')
# print('basic_pitch')
# evaluate('outputs/basic_pitch/*_transcription.mid',  '_transcription.mid', '.mid', "FiloBass/midi_fully_aligned", 'test')
# evaluate('outputs/basic_pitch/*_transcription.mid',  '_transcription.mid', '.mid', "FiloBass/midi_fully_aligned", 'test')

evaluate('outputs/crepe_notes_updated/*_transcription.mid',  '_transcription.mid', '.mid', "FiloBass/midi_fully_aligned", 'test')
