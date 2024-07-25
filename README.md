# Clip Cut App :scissors:


A Generative AI app in which you can generate an audio track with 
a text prompt and add it to one of your cut clips


#### The used generative model is Riffusion:

GitHub: https://github.com/riffusion/riffusion-hobby.git

*Riffusion is a library for real-time music and audio generation with stable diffusion.
Read about it at https://www.riffusion.com/about and try it at https://www.riffusion.com/.
This is the core repository for riffusion image and audio processing code.*

Related repositories:
* Web app: https://github.com/riffusion/riffusion-app
* Model checkpoint: https://huggingface.co/riffusion/riffusion-model-v1

## Run the app
###### Open your CMD and follow next steps:

1) Clone the github repository
```
git clone https://github.com/krichfalushy/ClipCut.git
```
2) Go to cloned directory
```
cd ClipCut
```
3) Create a virtual environment
```
 python -m venv .venv
```
4) Activate it
```
source .venv/bin/activate          #for macOs
.\.venv\Scripts\activate.bat       #for Windows
```
5) Install all dependencies
```
pip install -r requirements.txt
```

```
pip install -r requirements_clipcut.txt
```

*In order to use audio formats other than WAV, ffmpeg is required.*

```
sudo apt-get install ffmpeg          # linux 
brew install ffmpeg                  # mac
```

6) Run the app
```
streamlit run app.py --server.headless true
```

## Run with Docker
###### Open your CMD and follow next steps:

1) Run Docker Pull Command
```
docker pull krichfalushy/clipcut_app
```
2) Check all your images
```
docker images
```
3) Run pulled container
```
docker run -p 8501:8501 <container_id>
```

You can also check docker status:
`docker ps` or `docker logs <container_id>`

## Information
For more information about running riffusion check out
the links below
1) Riffusion/inference: https://github.com/riffusion/riffusion-hobby
2) Riffusion/app: https://github.com/riffusion/riffusion-app-hobby
3) Huggingface/diffusers: https://github.com/huggingface/diffusers
4) HuggingFace riffuson model: https://huggingface.co/riffusion/riffusion-model-v1
4) What is streamlit: https://docs.streamlit.io


## Backends

### CPU
`cpu` is supported but is quite slow.

### CUDA
`cuda` is the recommended and most performant backend.

To use with CUDA, make sure you have torch and torchaudio installed with CUDA support. See the
[install guide](https://pytorch.org/get-started/locally/) or
[stable wheels](https://download.pytorch.org/whl/torch_stable.html).

To generate audio in real-time, you need a GPU that can run stable diffusion with approximately 50
steps in under five seconds, such as a 3090 or A10G.
