# VivyGAN API

### This application is intended to be deployed on a Linux VM, as such you may encounter issues running it on Windows. If using Windows 10 or 11, consider setting up [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install) and installing it there.

This project should be used in conjunction with the [VivyGAN Front-End](https://github.com/MayeHunt/VivyGAN_Front).

API endpoints for the VivyGAN Front-End.
This is a Flask application that can be operated using any method for POST requests.

## Setup Guide
This application requires [Python 3.10](https://www.python.org/downloads/) or higher and [pip](https://pip.pypa.io/en/stable/installation/) be installed.
To use this application:

1. `git clone https://github.com/MayeHunt/VivyGAN_API.git` to clone this repo.
2. `cd VivyGAN_API` to change directory to the cloned directory.
3. Install required packages using: `pip install -r requirements.txt`. Some packages are quite large, ensure at least 1gb is free.
4. Install [FluidSynth](https://github.com/FluidSynth/fluidsynth/wiki/Download). (e.g on Ubuntu: `sudo apt-get install fluidsynth`)
5. Start the application using gunicorn on linux: `gunicorn --timeout 240 run:app` or Flask on windows: `python -m flask run -p 8000`.

The application will download necessary files, the model download is around 130mb so it may take a minute.

The application will now be ready to accept API calls from the [VivyGAN Front-End](https://github.com/MayeHunt/VivyGAN_Front).
