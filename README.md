# VivyGAN API

This project should be used in conjunction with the [VivyGAN Front-End](https://github.com/MayeHunt/VivyGAN_Front).

API endpoints for the VivyGAN Front-End.
This is a Flask application that can be operated using any method for POST requests.

## Setup Guide
To use this application:

1. `git clone https://github.com/MayeHunt/VivyGAN_API.git` to clone this repo.
2. `cd VivyGAN_API` to change directory to the cloned directory.
3. Activate the venv (Bash: `source venv/bin/activate` Powershell: `venv\bin\activate.ps1` CMD `.\venv\bin\activate`) **OR** use own Python interpreter.
4. Install required packages using: `pip install -r requirements.txt`
5. Start the application using gunicorn: `gunicorn --timeout 240 run:app`

The application will now be ready to accept API calls from the [VivyGAN Front-End](https://github.com/MayeHunt/VivyGAN_Front).
