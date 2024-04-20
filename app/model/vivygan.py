import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
import muspy
from azure.storage.blob import BlobServiceClient
import keras
import numpy as np
import tensorflow as tf


def generate_random(generator, batch_size=1000, latent_dim=100):
    noise = generate_noise(batch_size, latent_dim)
    generated_images = generator.predict(noise)
    binarized_images = (generated_images != 0).astype(int)

    muspy_music_objects = []
    for i in range(batch_size):
        prepared_image = np.squeeze(binarized_images[i], axis=-1)
        prepared_image = remove_short_notes(prepared_image).T
        music = convert_to_muspy_class(prepared_image)
        muspy_music_objects.append(music)

    # metrics function not made yet, return this randomly picked one
    generated_track = muspy_music_objects[6]
    return generated_track


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


def generate_noise(batch_size, latent_dim):
    return np.random.normal(0, 1, (batch_size, latent_dim))


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
