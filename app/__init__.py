from flask import Flask
from flask_cors import CORS
from .model.download_model import download_model_file

def create_app():
    app = Flask(__name__, static_folder='static', instance_relative_config=True)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_pyfile('config.py', silent=True)

    # real heroku blob connection
    # connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    # container_name = os.environ.get('MODEL_CONTAINER_NAME')
    # blob_name = os.environ.get('MODEL_BLOB_NAME')
    # model = download_model_file(connection_string, container_name, blob_name)

    # Temp testing blob connection
    model = download_model_file(
        app.config['AZURE_STORAGE_CONNECTION_STRING'],
        app.config['MODEL_CONTAINER_NAME'],
        app.config['MODEL_BLOB_NAME']
    )

    variation_model = download_model_file(
        app.config['AZURE_STORAGE_CONNECTION_STRING'],
        app.config['MODEL_CONTAINER_NAME'],
        app.config['MODEL_BLOB_NAME_2']
    )

    app.config['model'] = model
    app.config['variation_model'] = variation_model

    from . import routes
    app.register_blueprint(routes.bp)

    return app
