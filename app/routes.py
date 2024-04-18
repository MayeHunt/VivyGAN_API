from flask import Blueprint, current_app, send_file
import tempfile
import muspy
from .model.vivygan import generate_random

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/generate', methods=['POST'])
def generate():
    model = current_app.config['model']
    music_object = generate_random(model)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
        muspy.write_audio(tmp.name, music_object, audio_format='wav')
        tmp.seek(0)
        return send_file(tmp.name, mimetype='audio/wav', as_attachment=True, download_name='generated_track.wav')
