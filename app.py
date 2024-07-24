import io
import random
from pathlib import Path

import PIL
import streamlit as st
import tempfile
import os
import zipfile
import requests

from riffusion.spectrogram_image_converter import SpectrogramImageConverter
from riffusion.spectrogram_params import SpectrogramParams
import typing

os.environ["IMAGEIO_FFMPEG_EXE"] = r"/opt/homebrew/bin/ffmpeg"
# os.environ["IMAGEIO_FFMPEG_EXE"] = r"/urs/bin/ffmpeg"

from moviepy.editor import VideoFileClip, AudioFileClip, afx

from riffusion.server import compute_request
from riffusion.datatypes import PromptInput, InferenceInput, InferenceOutput
from riffusion.riffusion_pipeline import RiffusionPipeline


# Function to cut the video on slices
def split_video(path, num):
    video_f = VideoFileClip(path)
    clips = []
    duration = video_f.duration / num

    for i in range(num):
        start = i * duration
        end = (i + 1) * duration
        clips.append(video_f.subclip(start, end))

    return clips


# Adding generated audio to the clip
def add_audio(audio_f, clip_index):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(audio_f.getvalue())
        temp_audio = f.name

    audio_clip = AudioFileClip(temp_audio)
    temp_audio = tempfile.mktemp(suffix=".mp3")
    audio_clip.write_audiofile(temp_audio)

    video_clip = VideoFileClip(temp_paths[clip_index - 1])
    audio = afx.audio_loop(audio_clip, duration=video_clip.duration)

    new_clip = video_clip.set_audio(audio)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    new_clip.write_videofile(temp_file.name, codec='libx264', audio_codec='aac')

    return temp_file.name


# Функція, фактично копіює іншу - compute_request з модуля server.py, пакунку riffusion.
# Відмінність у тому, що ця функція повертає не JSON, а tuplet, що містить згенерований малюнок,
# згенерований mp3-файл  і його тривалість в секундах
def generate_audio_by_prompt(prompt):
    # let's change seed every time before composing input
    seed = random.randint(30, 3000)
    prompt_input = PromptInput(prompt=prompt, seed=seed, denoising=0.75, guidance=7.0)
    inference_input = InferenceInput(start=prompt_input, end=prompt_input, alpha=0)
    pipeline = RiffusionPipeline.load_checkpoint(
        checkpoint="riffusion/riffusion-model-v1",
        use_traced_unet=False,
        device="cpu",
    )
    # Load the seed image by ID
    init_image_path = Path("seed_images", f"{inference_input.seed_image_id}.png")

    if not init_image_path.is_file():
        return f"Invalid seed image: {inference_input.seed_image_id}", 400
    init_image = PIL.Image.open(str(init_image_path)).convert("RGB")

    # Load the mask image by ID
    mask_image: typing.Optional[PIL.Image.Image] = None
    if inference_input.mask_image_id:
        mask_image_path = Path("seed_images", f"{inference_input.mask_image_id}.png")
        if not mask_image_path.is_file():
            return f"Invalid mask image: {inference_input.mask_image_id}", 400
        mask_image = PIL.Image.open(str(mask_image_path)).convert("RGB")

    # Execute the model to get the spectrogram image
    generated_image = pipeline.riffuse(
        inference_input,
        init_image=init_image,
        mask_image=mask_image,
    )

    # TODO(hayk): Change the frequency range to [20, 20k] once the model is retrained
    params = SpectrogramParams(
        min_frequency=0,
        max_frequency=10000,
    )

    # Reconstruct audio from the image
    # TODO(hayk): It may help performance a bit to cache this object
    converter = SpectrogramImageConverter(params=params, device=str(pipeline.device))

    segment = converter.audio_from_spectrogram_image(
        generated_image,
        apply_filters=True,
    )

    # Export audio to MP3 bytes
    mp3_bytes = io.BytesIO()
    segment.export(mp3_bytes, format="mp3")
    mp3_bytes.seek(0)

    # Export image to JPEG bytes
    image_bytes = io.BytesIO()
    generated_image.save(image_bytes, exif=generated_image.getexif(), format="JPEG")
    image_bytes.seek(0)

    # Assemble the output dataclass
    return generated_image, mp3_bytes, segment.duration_seconds


# STYLE CODE
st.set_page_config(page_title="CLipCut", layout="wide")

st.title(":orange[# Clip Cut]")
st.write(" ")
text = st.write(f'''
#### Description
This is a Generative AI app\n
___Here you can___\n
• Cut your videos into ___maximum 20 pieces___.\n
• With a text prompt generate the audio to one of your cut clips.\n
• Choose the index number of clip you want add audio to.\n
• Chose the number of columns where you can review clips.\n
• And then download zip archive and enjoy your life :D
''')
st.write("---")


# 1 part of page
left_col, right_col = st.columns([1, 1])
with st.container():

    with left_col:
        uploaded_video = st.file_uploader("##### Upload the video", type=["mp4", "mov", "avi", "mkv"])
        clips_num = st.number_input("##### Number of clips to cut to", min_value=1, max_value=20, step=1)
        clip_index = st.number_input("##### Number of clip to add the audio to", min_value=1, max_value=20, step=1)
        columns_num = st.number_input("##### Number of columns for review", min_value=1, max_value=20, step=1)

    with right_col:
        st.write(" ")

        # Uploaded video review
        if uploaded_video:
            _, container, _ = st.columns([15, 80, 15])
            container.video(uploaded_video)


# 2 part of page
with st.container():
    st.write(" ")
    _, centre, _ = st.columns([1, 3, 1])

    with centre:
        st.write(" ")
        st.write("### Write any theme for audio generation")
        prompt = st.text_input(label="___Write a prompt, for example: 'flowers song'___")
        button = st.button("Start generation")
        st.write(" ")


st.write("---")
st.write(" ")
st.write("### Your video clips")


# 3 part of page
if button and uploaded_video and prompt and clip_index <= clips_num:

    # Generated audio to the clip_index video
    image, mp3_bytes, duration = generate_audio_by_prompt(prompt)

    with st.container(height=500):
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(uploaded_video.read())
            temp_file = f.name

        video = VideoFileClip(temp_file)
        temp_output = tempfile.mktemp(suffix=".mp4")
        video.write_videofile(temp_output, codec="libx264", audio_codec="aac")

        # List of clips
        clips = split_video(temp_file, clips_num)
        _, container, _ = st.columns([15, 80, 15])

        # Creating temporary clip paths list
        temp_paths = []
        for i, clip in enumerate(clips):
            temp_clip = os.path.join(tempfile.gettempdir(), f"clip_{i + 1}.mp4")
            clip.write_videofile(temp_clip, codec="libx264", audio_codec="aac")
            temp_paths.append(temp_clip)

        # Adding an audio
        temp_file = add_audio(mp3_bytes, clip_index=clip_index)
        temp_paths[clip_index - 1] = temp_file

        # Video by columns
        # with st.expander("## Your video clips", expanded=True):
        for i in range(0, len(temp_paths), columns_num):
            cols = st.columns(columns_num)
            for j, col in enumerate(cols):
                if i + j < len(temp_paths):
                    col.video(temp_paths[i + j])

        # Download the archive
        zip_path = os.path.join(tempfile.gettempdir(), "clips.zip")
        with zipfile.ZipFile(zip_path, "w") as f:
            for path in temp_paths:
                f.write(path, arcname=os.path.basename(path))

        with open(zip_path, "rb") as f:
            st.download_button(label="Download the clips archive",
                               data=f,
                               file_name="clips.zip")

    # 4 part of page
    with st.container():
        # We can also show generated image here if it necessary
        # st.image(image)

        st.write(" ")

        # extension = "mp3"
        # mp3_name = f"{prompt.replace(' ', '_')}.{extension}"
        # st.download_button(
        #     mp3_name,
        #     data=mp3_bytes,
        #     file_name=mp3_name,
        #     mime=f"audio/{extension}",
        # )

        st.write("### Generated audio")
        st.audio(mp3_bytes)




