# ODS-Praktikum-Big-Brother
Repository for the Group Project "Big Brother" at TU Berlin  
The comments, code and documentation is written in english. We only use german
if there isn't any other way.

# Getting Started

<<<<<<< HEAD
## Understanding the project
1. Setup ssh-key.
2. Clone repository into your local folder (`git clone <ssh-url>`)
3. **Read our contribution guidelines [here](./CONTRIBUTING.md)!**
4. Browse through our [documentation](#documentation)

## Project setup
You have a few options when executing the project locally. You can run it in
the docker container or install the packages locally (in an environmen for 
instance) to run the flask server. Be aware that the docker container takes
quite some time to build. Most of the time it would be more practical to have
a python environment setup.

### Docker
In this case you only need to setup docker. You may either use a docker GUI
or the CLI. In case you use the CLI:
1. To into the root of the git repository.
3. Execute `docker build -t bigbrother .`. This takes quite a long time and 
requires an internet connection.
4. Execute `docker run -p 3000:3000 bigbrother:latest`. The `3000` refers to
the port exposed in the docker container and the second `3000` is the port
that you expose locally.
5. After waiting for a few seconds you should be able to go to `127.0.0.1:3000`
in your browser and use the website.

### Local packages
You can also do the following steps in an environment. It's important to mention
again that we use **Python 3.10**. Other versions are not guaranteed to work,
although you are welcome to try in future iterations of the project. All steps 
where you use the commandline are executed inside of the root directory of the
git repository:
1. Install **Python 3.10**. Make sure that you also have the package manager
pip installed. This should be the case if you installed python with the 
installer from the official website.
2. You might need to install the visual c++ redistributables if you are working
on windows: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170
3. Install dlib. You can execute either of those:
    - `pip install make cmake` and then `pip install dlib`
    - `pip install make cmake` and then `pip install dlib-binary`
    - Build it directly from the source
4. Install the rest of the requirements with `pip install -r requirements.txt`.
5. Execute `python ./src/bigbrother/run.py` to start the flask app. You can 
then go to `127.0.0.1:3000` in your webbrowser.

=======
## Setup 
1. Setup ssh-key and clone repository into your local folder (`git clone <ssh-url>`), or just clone using https: `git clone <https-url>`.
2. **Read our contribution guidelines [here](./CONTRIBUTING.md)!**
3. Browse through our [documentation](#documentation)
4. Setup the project either via Docker or in a local python environment. Most of the time it would be more practical to have
a python environment setup.


### Docker
Installing via Docker **doesn't** work on macOS or Windows. Otherwise the docker setup is pretty straightforward. You may either use the docker desktop GUI. Be aware that the docker container takes quite some time to build.
or the CLI. In case you use the CLI:
1. Open a terminal in the root of the git repository.
2. Execute `docker build -t bigbrother .`. This takes quite a long time and 
requires an internet connection. 
3. Execute `docker run -p 3000:3000 bigbrother:latest`. The `3000` refers to
the port exposed in the docker container and the second `3000` is the port
that you expose locally.
4. After waiting for a few seconds you should be able to go to `127.0.0.1:3000`
in your browser and use the website.


### Local packages
It's important to mention again that we use **Python 3.10**. Other versions are not guaranteed to work,
although you are welcome to try in future iterations of the project. All steps 
where you use the commandline are executed inside of the root directory of the

#### Installation on Windows
0. We would recommend to use WSL to emulate a Linux enviroment and install this project using the Linux steps. If you don't want to do that, continue here.
1. You need to have Visual Studio and it's C++ Desktop Package installed. 
2. Install MongoDB Community Server and make sure that it's active. Important when trying to start the WebApp. 
3. Install **Python 3.10**. The packges manager pip should be installed alongside Python automatically.
4. Install CMake and Git if you haven't already. Restart your PC to make sure that your PATH gets properly updated.
5. Clone the repository into your folder.
5. Create a Python virtual environment (optional but highly recommended) using `python -m venv .env`. The name .env is preferred since it's already listed in .gitignore. To activate it, run `.env\Scripts\Activate.ps1` (PowerShell), `.env\Scripts\activate.bat` (Command Prompt) or `source .env/Scripts/activate` (Git Bash).
6. Manually install dlib: `pip install dlib-binary`
7. Install  the requirements with `pip install -r requirements.txt`.
8. Execute `python ./src/bigbrother/run.py` to start the flask app. You can 
then go to `127.0.0.1:3000` in your webbrowser.

#### Installation on macOS
1. Make sure you have homebrew installed, then `brew install cmake` and `brew install libpng`.
2. Install MongoDB-Community and make sure that it's active with `brew services start mongodb-community`
3. Install **Python 3.10**, `brew install python@3.10`. The package manager pip should be automatically installed as well.
4. Create a python virtual enviroment (optional but highly recommended) `python3.10 -m venv .env`. Keep the name `.env` since that's ignored in the .gitignore. Make sure to activate the virtual enviroment `source .env/bin/activate`.
5. Install the requirements with `pip install -r requirements.txt`.
6. Execute `python ./src/bigbrother/run.py` to start the flask app. You can 
then go to `127.0.0.1:3000` in your webbrowser.


#### Installation on Linux (untested)


>>>>>>> EduVids-Completing
# Documentation
We have a documentation in the [docs](docs/)-folder. We highly recommend you to
at least skim through the documetnation in order to get a grasp of the project.
And the folder structure that we decided upon if you want to contribute to/extend
the codebase.

# Tool stack
- Programming language: Python 3.10
- Frontend: [Flask](https://flask.palletsprojects.com/en/2.2.x/) Docker
- FaceRecognition and other ML-libraries: 
    - [openCV](https://pypi.org/project/opencv-python/)
    - [OpenFace](https://cmusatyalab.github.io/openface/)
    - [PyTorch](https://pytorch.org/)
    - [TensorFlow](https://www.tensorflow.org/learn)
- Database: [MongoDB](https://www.mongodb.com/)

# Benchmark
## Gesture Recognition
The Benchmark loads the trained model from checkpoint and evaluate it. You can also use it to finetune the model.   
Go to benchmarks/gesture_recognition and RUN: 
` docker build -t gesture-recognition .`
`docker run --gpus all -v $(pwd):/app -it gesture-recognition`
`python benchmark2.py`
