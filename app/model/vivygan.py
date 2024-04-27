import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
import muspy
import numpy as np
import tensorflow as tf
from keras.preprocessing.image import load_img, img_to_array
import pretty_midi
from pypianoroll import Multitrack, Track
from PIL import Image
import matplotlib.pyplot as plt


def generate_random(generator, batch_size=500, latent_dim=100, choose_arbitrary=False, scale=None, shift_pitch=False, cut_notes=False, equal_weights=False, least_dissonant=False):
    noise = generate_noise(batch_size, latent_dim)
    generated_images = generator.predict(noise)
    binarized_images = (generated_images != 0).astype(int)

    track_array = []
    muspy_music_objects = []
    for i in range(batch_size):
        prepared_image = np.squeeze(binarized_images[i], axis=-1)
        prepared_image = remove_short_notes(prepared_image).T
        track_array.append(prepared_image)
        music = convert_to_muspy_class(prepared_image)
        if cut_notes:
            music = remove_lowest_notes_by_percentage(music, 60)
        muspy_music_objects.append(music)

    if choose_arbitrary:
        return muspy_music_objects[6]
    elif scale is not None:
        generated_track, index_value = find_best_sample(muspy_music_objects, scale=scale)
        return generated_track
    elif shift_pitch:
        # function to shift the pitch rather than the muspy pitch function
        return None
    elif equal_weights and least_dissonant:
        _, _, top_dissonant = find_least_dissonant(muspy_music_objects)
        generated_track, index_value = find_best_sample(top_dissonant)
        return generated_track
    elif equal_weights:
        generated_track, index_value = find_best_sample(muspy_music_objects)
        return generated_track
    elif least_dissonant:
        generated_track, index_value, top_dissonant = find_least_dissonant(muspy_music_objects)
        return generated_track
    else:
        generated_track, index_value, top_dissonant = find_least_dissonant(muspy_music_objects)
    return generated_track


def generate_random_variations(generator, file_path, batch_size=10):
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        original = load_from_png(file_path)
    elif file_path.lower().endswith(('.mid', '.midi')):
        original = load_from_midi(file_path)
    elif file_path.lower().endswith(('.npz', '.npy')):
        original = load_from_pianoroll(file_path)

    music_array = []
    outputs = []
    for i in range(batch_size):
        noise = original + np.random.normal(0, 0.1, original.shape)
        generated_image = generator.predict(noise[np.newaxis, :])
        binarized_image = (generated_image > 0.5).astype(np.float32)
        prepared_image = np.squeeze(binarized_image, axis=-1)
        prepared_image = np.squeeze(prepared_image)
        prepared_image = remove_short_notes(prepared_image).T
        music_array.append(prepared_image)
        music = convert_to_muspy_class(prepared_image)
        outputs.append(music)
    # save_imgs(music_array, file_name='variation')
    return outputs


def generate_noise(batch_size, latent_dim):
    return np.random.normal(0, 1, (batch_size, latent_dim))


def convert_to_muspy_class(track_array, time_unit=1, pitch_offset=24):
    music = muspy.Music()
    track = muspy.Track(program=0, is_drum=False)
    note_start_times = [-1] * len(
        track_array[0])

    for time, pitch_row in enumerate(track_array):
        for pitch, active in enumerate(pitch_row):
            current_pitch = pitch + pitch_offset
            if active == 1 and note_start_times[pitch] == -1:
                note_start_times[pitch] = time
            elif active == 0 and note_start_times[pitch] != -1:
                duration = time - note_start_times[pitch]
                note = muspy.Note(
                    pitch=current_pitch,
                    time=note_start_times[pitch] * time_unit,
                    duration=duration * time_unit,
                    velocity=100
                )
                track.notes.append(note)
                note_start_times[pitch] = -1

    for pitch, start_time in enumerate(note_start_times):
        if start_time != -1:
            duration = len(track_array) - start_time
            note = muspy.Note(
                pitch=pitch + pitch_offset,
                time=start_time * time_unit,
                duration=duration * time_unit,
                velocity=100
            )
            track.notes.append(note)
    music.tracks.append(track)
    return music


def remove_short_notes(image, threshold=12):
    for pitch in range(image.shape[0]):
        active_note_start = None
        for time_step in range(image.shape[1]):
            if image[pitch, time_step] == 1 and active_note_start is None:
                # note start
                active_note_start = time_step
            elif image[pitch, time_step] == 0 and active_note_start is not None:
                # note end
                if time_step - active_note_start < threshold:
                    image[pitch, active_note_start:time_step] = 0
                active_note_start = None
        # last note
        if active_note_start is not None and image.shape[1] - active_note_start < threshold:
            image[pitch, active_note_start:] = 0
    return image


def remove_notes_below_C2(music):
    C2_MIDI_NUMBER = 48
    for track in music.tracks:
        track.notes = [note for note in track.notes if note.pitch >= C2_MIDI_NUMBER]
    return music


def remove_lowest_notes_by_percentage(music, percentage):
    for track in music.tracks:
        notes = [(note.time, note.time + note.duration, note.pitch) for note in track.notes]
        notes.sort(key=lambda x: x[2])
        number_to_remove = int(len(notes) * (percentage / 100.0))
        notes_to_remove = set(notes[:number_to_remove])
        track.notes = [note for note in track.notes if (note.time, note.time + note.duration, note.pitch) not in notes_to_remove]
    return music


def find_least_dissonant(tracks):
    dissonance_scores = {}

    for i, track in enumerate(tracks):
        dissonance_scores[i] = dissonance_rate(track)

    def get_top_scores(scores, top_n=100, reverse=False):
        return dict(sorted(scores.items(), key=lambda item: item[1], reverse=reverse)[:top_n])

    top_dissonance = get_top_scores(dissonance_scores)  # lower is better

    average_ranks = {}
    for i in range(len(tracks)):
        ranks = [
            list(top_dissonance.keys()).index(i) if i in top_dissonance else len(tracks)
        ]
        average_ranks[i] = ranks

    best_track_index = min(average_ranks, key=average_ranks.get)
    print(f"Best track found: Index {best_track_index}")
    top_dissonant_tracks = [tracks[i] for i in top_dissonance if i in top_dissonance]
    return tracks[best_track_index], best_track_index, top_dissonant_tracks


def find_best_sample(tracks, scale=None):
    polyphony_scores, scale_consistency_scores, pitch_entropy_scores, dissonance_scores = {}, {}, {}, {}
    scale_scores = {}
    total_tracks = len(tracks)
    print(f"Starting metrics calculation for {total_tracks} tracks.")

    for i, track in enumerate(tracks):
        if i % 100 == 0:
            print(f"Processing track {i + 1}/{total_tracks}...")
        polyphony = muspy.polyphony(track)
        if polyphony >= 1:
            polyphony_scores[i] = polyphony
        else:
            polyphony_scores[i] = 10  # As I want constant notes, there should always be one note playing
        scale_consistency_scores[i] = muspy.scale_consistency(track)
        pitch_entropy_scores[i] = muspy.pitch_entropy(track)
        dissonance_scores[i] = dissonance_rate(track)
        if scale is not None:
            scale_scores[i] = muspy.pitch_in_scale_rate(track, scale[0], scale[1])

    def get_top_scores(scores, top_n=100, reverse=False):
        return dict(sorted(scores.items(), key=lambda item: item[1], reverse=reverse)[:top_n])

    print("Sorting and ranking tracks...")
    top_polyphony = get_top_scores(polyphony_scores)  # Lower is better
    top_scale_consistency = get_top_scores(scale_consistency_scores, reverse=True)  # Higher is better
    top_pitch_entropy = get_top_scores(pitch_entropy_scores)  # Lower is better
    if scale is not None:
        top_in_scale_rate = get_top_scores(scale_scores, reverse=True)  # Higher is better
        filtered_top_in_scale_rate = {k: v for k, v in top_in_scale_rate.items() if v > 0.80}  # only take tracks with 80% in scale rate
        print(filtered_top_in_scale_rate)
        if filtered_top_in_scale_rate is None:
            filtered_top_in_scale_rate = {k: v for k, v in top_in_scale_rate.items() if v > 0.70}  # expanding criteria to 70%
    top_dissonance = get_top_scores(dissonance_scores)  # lower is better


    print("Calculating average ranks...")
    average_ranks = {}
    if scale is not None:
        for i in range(len(tracks)):
            if i in filtered_top_in_scale_rate:
                ranks = [
                    list(top_polyphony.keys()).index(i) if i in top_polyphony else len(tracks),
                    list(top_scale_consistency.keys()).index(i) if i in top_scale_consistency else len(tracks),
                    list(top_pitch_entropy.keys()).index(i) if i in top_pitch_entropy else len(tracks),
                    list(top_dissonance.keys()).index(i) if i in top_dissonance else len(tracks)
                ]
                average_ranks[i] = np.mean(ranks)
    else:
        for i in range(len(tracks)):
            ranks = [
                list(top_polyphony.keys()).index(i) if i in top_polyphony else len(tracks),
                list(top_scale_consistency.keys()).index(i) if i in top_scale_consistency else len(tracks),
                list(top_pitch_entropy.keys()).index(i) if i in top_pitch_entropy else len(tracks),
                list(top_dissonance.keys()).index(i) if i in top_dissonance else len(tracks)
            ]
            average_ranks[i] = np.mean(ranks)

    best_track_index = min(average_ranks, key=average_ranks.get)
    print(f"Best track found: Index {best_track_index}")
    return tracks[best_track_index], best_track_index


def dissonance_rate(music):
    total_intervals = 0
    dissonant_count = 0
    dissonant_intervals = {1, 2, 6, 10, 11}

    for track in music.tracks:
        previous_note = None
        for note in sorted(track.notes, key=lambda x: x.start):
            if previous_note:
                interval = abs(note.pitch - previous_note.pitch) % 12
                if interval in dissonant_intervals:
                    dissonant_count += 1
                total_intervals += 1
            previous_note = note

    if total_intervals == 0:
        return 0

    return dissonant_count / total_intervals


def load_from_png(file_path, target_size=(72, 384)):
    img = load_img(file_path, color_mode='grayscale', target_size=target_size)
    img_array = img_to_array(img)
    img_array = img_array / 255.0
    return img_array.squeeze()


def load_from_midi(midi_file, fs=100, pitch_range=(0, 72)):
    midi_data = pretty_midi.PrettyMIDI(midi_file)
    piano_roll = midi_data.get_piano_roll(fs=fs)[pitch_range[0]:pitch_range[1], :]
    piano_roll = np.where(piano_roll > 0, 1, 0)
    return piano_roll


def load_from_pianoroll(file_path, track_index=0, binarize=True):
    multitrack = Multitrack(file_path)
    track = multitrack.tracks[track_index]
    piano_roll = track.pianoroll
    if binarize:
        piano_roll = np.where(piano_roll > 0, 1, 0)
    return piano_roll


def save_imgs(generated_images, file_name, save_dir='./static', save_file=True):
    if len(generated_images) == 1:
        generated_images = [generated_images]

    for i, img in enumerate(generated_images):
        img = np.squeeze(img)

        img = (img - np.min(img)) / (np.max(img) - np.min(img)) * 255
        img = img.astype(np.uint8)

        img = Image.fromarray(img, 'L')
        if save_file:
            img.save(f'{save_dir}/{file_name}_{i+1}.png')

    if img:
        return img
