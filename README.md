# ODS-Praktikum-Big-Brother
Repository for the Group Project "Big Brother" at TU Berlin  
The comments, code and documentation is written in english. We only use german
if there isn't any other way.

# Getting Started

## Understanding the project
1. Setup ssh-key.
2. Clone repository into your local folder (`git clone <ssh-url>`)
3. **Read our contribution guidelines [here](./CONTRIBUTING.md)!**
4. Browse through our [documentation](#documentation)

## Project setup
You have a few options when executing the project locally. You can run it in
the docker container or install the packages locally (in an environment for 
instance) to run the flask server. Be aware that the docker container takes
quite some time to build. Most of the time it would be more practical to have
a python environment setup.

### Docker
The docker setup is pretty straightforward. You may either use the docker desktop GUI
or the CLI. In case you use the CLI:
1. To into the root of the git repository.
2. Execute `docker build -t bigbrother .`. This takes quite a long time and 
requires an internet connection. **Warning:** If you are on an apple silicon mac, this **doesn't** work since some packages are only available for x86_64 and macOS arm, NOT for the emulated linux arm that docker uses. You can avoid that problem by forcing docker to compile for x86_64 and then use rosetta to still make it work on mac:  `docker build --platform=linux/x86_64 -t bigbrother .`
3. Execute `docker run -p 3000:3000 bigbrother:latest`. The `3000` refers to
the port exposed in the docker container and the second `3000` is the port
that you expose locally.
4. After waiting for a few seconds you should be able to go to `127.0.0.1:3000`
in your browser and use the website.


### Local packages
It's important to mention again that we use **Python 3.10**. Other versions are not guaranteed to work,
although you are welcome to try in future iterations of the project. All steps 
where you use the commandline are executed inside of the root directory of the

git repository:
1. If you are on **windows**: You need to have the visual c++ redistributables https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170 installed. 
2. Install MongoDB and make sure that it's active. Important when trying to start the WebApp. 
3. Install **Python 3.10**. Make sure that you also have the package manager
pip installed. This should be the case if you installed python with the 
installer from the official website.
4. Create a python virtual enviroment (highly recommended) and call it ".env" which is already set to be ignored in the .gitignore. Make sure to activate the virtual env.
5. Install  the requirements with `pip install -r requirements.txt`. If you are on **windows**: manually install dlib: pip install dlib-binary
6. Execute `python ./src/bigbrother/run.py` to start the flask app. You can 
then go to `127.0.0.1:3000` in your webbrowser.

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
