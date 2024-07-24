import requests
import streamlit as st
import tempfile

# from riffusion_hobby.riffusion.streamlit.tasks import text_to_audio as tta
#
#
# result = tta.render()


'''
in terminal:
    mkdir riffusion_dir
    cd riffusion_dir
    python3.10 -m venv venv
    source venv/bin/activate
    git clone https://github.com/riffusion/riffusion-hobby.git
    pip install -r requirements.txt
    pip install -r requirements_dev.txt
        cd riffusion_dir
        git clone https://github.com/riffusion/riffusion-app-hobby.git
        create .env.local file with RIFFUSION_FLASK_URL=http://127.0.0.1:3013/run_inference/ in
        npm install
    cd riffusion_dir
    python -m riffusion.server --port 3013 --host 127.0.0.1
    < Running on http://127.0.0.1:3013 >
        npm run dev
        < ready - started server on 0.0.0.0:3000, url: http://localhost:3000 >
'''


prompt = "cow"
duration = 15


def generate_audio(prompt):
    url = r"http://localhost:3000"

    payload = {
        "prompt": prompt,
    }

    response = requests.post(url, payload)
    if response.status_code == 200:
        audio_path = tempfile.mktemp(suffix=".wav")
        with open(audio_path, 'wb') as f:
            f.write(response.content)
        return audio_path
    else:
        st.error("Error")
        return None


print(generate_audio(prompt))


