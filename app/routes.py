from flask import Blueprint, request, jsonify
from .utils import generate_piano_roll

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/generate', methods=['POST'])
def generate():
    # Here you would extract data from request if necessary
    audio_url = generate_piano_roll()
    return jsonify({'audio_url': audio_url})
