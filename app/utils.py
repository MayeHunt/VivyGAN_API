from .model import wgan_gp_model

def generate_piano_roll():
    # Generate piano roll using the model
    piano_roll = wgan_gp_model.generate()
    audio_url = wgan_gp_model.convert_to_audio(piano_roll)
    return audio_url
