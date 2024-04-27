from flask import Blueprint, current_app, jsonify, send_from_directory, request
from flask_cors import CORS
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


@bp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response


@bp.route('/static/<path:filename>')
def custom_static(filename):
    response = send_from_directory(bp.static_folder, filename)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@bp.route('/generate', methods=['POST'])  # default generate with a mixture of metrics
def generate():
    model = current_app.config['model']
    music_object = generate_random(model, cut_notes=True, equal_weights=True, least_dissonant=True)

    static_dir = os.path.join(current_app.root_path, 'static')
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

    response = jsonify({
        'audio_url': audio_url,
        'image_url': image_url,
        'message': 'Files successfully generated.'
    })
    return response


@bp.route('/generate_60_percent', methods=['POST'])  # cutting the total number of notes by 60% starting from low notes
def generate_percentage_cut():
    model = current_app.config['model']
    music_object = generate_random(model, cut_notes=True)

    static_dir = os.path.join(current_app.root_path, 'static')
    audio_filename = '60_percent_cut_track.wav'
    image_filename = '60_percent_cut_track_pianoroll.png'

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


@bp.route('/generate_equal_weights', methods=['POST'])  # assigns equal weights to muspy polyphony, scale consistency, and pitch entropy along with the dissonance metric to find the best track
def generate_equal_weights():
    model = current_app.config['model']
    music_object = generate_random(model, equal_weights=True)

    static_dir = os.path.join(current_app.root_path, 'static')
    audio_filename = 'equal_weights_track.wav'
    image_filename = 'equal_weights_track_pianoroll.png'

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


@bp.route('/generate_low_dissonance', methods=['POST'])  # uses the dissonance metric to find the best track
def generate_least_dissonant():
    model = current_app.config['model']
    music_object = generate_random(model, least_dissonant=True)

    static_dir = os.path.join(current_app.root_path, 'static')
    audio_filename = 'lowest_dissonance_track.wav'
    image_filename = 'lowest_dissonance_track_pianoroll.png'

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


@bp.route('/generate_random', methods=['POST'])  # returns an arbitrary generation, for purely random comparison
def generate_true_random():
    model = current_app.config['model']
    music_object = generate_random(model, choose_arbitrary=True)

    static_dir = os.path.join(current_app.root_path, 'static')
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


@bp.route('/generate_to_scale', methods=['POST'])  # uses muspy pitch_in_scale_rate to find generated samples that best fit a desired scale
def generate_to_scale():
    data = request.get_json()
    note = data['note']
    mode = data['mode']
    octave = int(data['octave'])
    model = current_app.config['model']

    static_dir = os.path.join(current_app.root_path, 'static')
    audio_filename = f'{note}_scale_track.wav'
    image_filename = f'{note}_scale_track_pianoroll.png'

    note_to_midibase = {
        'C': 60, 'D': 62, 'E': 64, 'F': 65,
        'G': 67, 'A': 69, 'B': 71
    }

    midi_base = note_to_midibase[note]
    midi_note = midi_base + (octave - 4) * 12

    music_object = generate_random(model, scale=[midi_note, mode])

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


@bp.route('/generate_variations', methods=['POST'])  # uses a separate model to generate variations on samples by adding noise
def generate_variations():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if 'batch_size' not in request.form:
        return jsonify({"message": "Batch size not specified"}), 400
    batch_size = int(request.form['batch_size'])

    if not os.path.exists('upload'):
        os.makedirs('upload')

    filename = secure_filename(file.filename)
    file_path = os.path.join('upload', filename)
    file.save(file_path)

    model = current_app.config['variation_model']
    music_objects = generate_random_variations(model, file_path, batch_size=batch_size)

    static_dir = os.path.join(current_app.root_path, 'static')

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
