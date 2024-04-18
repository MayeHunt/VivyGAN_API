import os
import muspy
from azure.storage.blob import BlobServiceClient
import keras
import numpy as np


def generate_random(generator, batch_size=1000, latent_dim=100):
    noise = generate_noise(batch_size, latent_dim)
    generated_images = generator.predict(noise)

    binarized_images = (generated_images != 0).astype(int)
    print(binarized_images[0].shape)

    muspy_music_objects = []
    for i in range(batch_size):
        prepared_image = np.squeeze(binarized_images[i], axis=-1).T

        music = convert_to_muspy_class(prepared_image)
        muspy_music_objects.append(music)

    # metrics function not made yet, return this randomly picked one
    generated_track = muspy_music_objects[6]

    return generated_track


def convert_to_muspy_class(track_array, time_unit=1, pitch_offset=24):
    music = muspy.Music()
    track = muspy.Track(program=0, is_drum=False)
    for time, pitch_row in enumerate(track_array):
        for pitch, active in enumerate(pitch_row):
            if (active == 1).any():
                note = muspy.Note(
                    pitch=pitch + pitch_offset,
                    time=time * time_unit,
                    duration=time_unit,
                    velocity=100
                )
                track.notes.append(note)
    music.tracks.append(track)
    return music


def generate_noise(batch_size, latent_dim):
    return np.random.normal(0, 1, (batch_size, latent_dim))
