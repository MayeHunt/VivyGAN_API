from flask import Blueprint, current_app, send_file, jsonify, send_from_directory, request
import tempfile
import muspy
from .model.vivygan import generate_random
import pypianoroll
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import os
import matplotlib.pyplot as plt


bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/generate', methods=['POST'])
def generate():
    model = current_app.config['model']
    music_object = generate_random(model)

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


def save_pianoroll_image(music_object, filename):
    muspy.show_pianoroll(music_object)
    plt.savefig(filename)
    plt.close()