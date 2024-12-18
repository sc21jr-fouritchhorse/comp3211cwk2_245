FUNCTION APP
NOTE: The requirements.txt provided within the directory captioner_functionapp
is not nessacary for local use. Install all packages using the requirements.txt
in the current venv .comp3211cwk2. in this directory
Moondream model also needs to be installed from https://ollama.com/library/moondream/blobs/e554c6b9de01
to get GetCaption to work

FRONTEND INSTRUCTIONS
Steps to running the flask application after cd-ing into comp3211_frontend/
1. Enter the venv using 
   `source ../.comp3211cwk2/bin/activate` 
2. Install redis-server
   `sudo <your_package_manager> install redis-server`
3. Start a redis-server in the command line (in case a server is not already running)
    `redis-server`
4. Open another terminal tab and run the command
    `celery -A celery_worker worker --loglevel=info`
5.  In an additional termnial tab run the flask app using 
    `python app.py`