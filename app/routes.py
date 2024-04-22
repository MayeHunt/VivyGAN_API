from flask import Blueprint, current_app, send_file, jsonify, send_from_directory, request
from werkzeug.utils import secure_filename
import tempfile
import muspy
from .model.vivygan import generate_random, generate_random_variations
import pypianoroll
import numpy as np
import os
import matplotlib.pyplot as plt

muspy.download_musescore_soundfont()
bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/generate', methods=['POST'])
def generate():
    model = current_app.config['model']
    music_object = generate_random(model, choose_arbitrary=False)

    static_dir = 'static'
    audio_filename = 'track.wav'
    image_filename = 'track_pianoroll.png'

    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    audio_path = os.path.join(static_dir, audio_filename)
    muspy.write_audio(audio_path, music_object, audio_format='wav')
    image_path = os.path.join(static_dir, image_filename)
    save_pianoroll_image(music_object, image_path)
    audio_url = f"{request.host_url}static/{audio_filename}"
    image_url = f"{request.host_url}static/{image_filename}"

    return jsonify({
        'audio_url': audio_url,
        'image_url': image_url,
        'message': 'Files successfully generated.'
    })


@bp.route('/generate_random', methods=['POST'])
def generate_true_random():
    model = current_app.config['model']
    music_object = generate_random(model, choose_arbitrary=True)

    static_dir = 'static'
    audio_filename = 'random_track.wav'
    image_filename = 'random_track_pianoroll.png'

    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    audio_path = os.path.join(static_dir, audio_filename)
    muspy.write_audio(audio_path, music_object, audio_format='wav')
    image_path = os.path.join(static_dir, image_filename)
    save_pianoroll_image(music_object, image_path)
    audio_url = f"{request.host_url}static/{audio_filename}"
    image_url = f"{request.host_url}static/{image_filename}"

    return jsonify({
        'audio_url': audio_url,
        'image_url': image_url,
        'message': 'Files successfully generated.'
    })


@bp.route('/test', methods=['POST'])
def test_route():
    return jsonify({'status': 'success', 'message': 'Endpoint is reachable'})


@bp.route('/generate_to_scale', methods=['POST'])
def generate_to_scale():
    note = request.form['note']
    mode = request.form['mode']
    octave = int(request.form['octave'])
    model = current_app.config['model']

    static_dir = 'static'
    audio_filename = f'{note}_scale_track.wav'
    image_filename = f'{note}_scale_track_pianoroll.png'

    note_to_midibase = {
        'C': 60, 'D': 62, 'E': 64, 'F': 65,
        'G': 67, 'A': 69, 'B': 71
    }

    midi_base = note_to_midibase[note]
    midi_note = midi_base + (octave - 4) * 12

    music_object = generate_random(model, choose_arbitrary=False, scale=[midi_note, mode])

    audio_path = os.path.join(static_dir, audio_filename)
    muspy.write_audio(audio_path, music_object, audio_format='wav')
    image_path = os.path.join(static_dir, image_filename)
    save_pianoroll_image(music_object, image_path)
    audio_url = f"{request.host_url}static/{audio_filename}"
    image_url = f"{request.host_url}static/{image_filename}"

    return jsonify({
        'status': 'success',
        'message': 'Scale generated successfully.',
        'audio_url': audio_url,
        'image_url': image_url
    })


@bp.route('/generate_variations', methods=['POST'])
def generate_variations():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if 'batch_size' not in request.form:
        return jsonify({"message": "Batch size not specified"}), 400
    batch_size = int(request.form['batch_size'])

    filename = secure_filename(file.filename)
    file_path = os.path.join('upload', filename)
    file.save(file_path)

    model = current_app.config['variation_model']
    music_objects = generate_random_variations(model, file_path, batch_size=batch_size)

    static_dir = 'static'

    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    for i, music_object in enumerate(music_objects):
        audio_filename = f'variation_{i + 1}.wav'
        image_filename = f'variation_{i + 1}_pianoroll.png'

        audio_path = os.path.join(static_dir, audio_filename)
        muspy.write_audio(audio_path, music_object, audio_format='wav')

        image_path = os.path.join(static_dir, image_filename)
        save_pianoroll_image(music_object, image_path)

    audio_urls = [f"{request.host_url}static/variation_{i+1}.wav" for i in range(batch_size)]
    image_urls = [f"{request.host_url}static/variation_{i+1}_pianoroll.png" for i in range(batch_size)]

    return jsonify({
        'audio_urls': audio_urls,
        'image_urls': image_urls,
        'message': 'Files successfully generated.'
    })


def save_pianoroll_image(music_object, filename):
    muspy.show_pianoroll(music_object)
    plt.savefig(filename)
    plt.close()