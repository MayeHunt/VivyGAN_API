import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
from azure.storage.blob import BlobServiceClient
import keras


def download_model_file(connection_string, container_name, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    with open("model_save.keras", "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

    return keras.models.load_model('model_save.keras')
