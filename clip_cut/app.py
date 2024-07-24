import streamlit as st
import tempfile
import os
import zipfile
import requests


os.environ["IMAGEIO_FFMPEG_EXE"] = r"/opt/homebrew/bin/ffmpeg"

from moviepy.editor import VideoFileClip, AudioFileClip


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
def add_audio(clip, audio_file):
    audio = AudioFileClip(audio_file)
    new_clip = clip.set_audio(audio)
    return new_clip


# STYLE CODE
st.set_page_config(page_title="CLipCut", layout="wide")

st.title(":orange[# Clip Cut]")
st.write(" ")
text = st.write(f'''
#### Description
This is a Generative AI app \n
___Here you can___ \n
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
    # st.write("### Write any theme for audio generation")

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
with st.container(height=500):
    if button and uploaded_video and prompt:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(uploaded_video.read())
            temp_file = f.name

        video = VideoFileClip(temp_file)
        temp_output = tempfile.mktemp(suffix=".mp4")
        video.write_videofile(temp_output, codec="libx264", audio_codec="aac")

        # List of clips
        clips = split_video(temp_file, clips_num)
        _, container, _ = st.columns([15, 80, 15])

        # Generate audio for the clip_index video
        from riffusion_hobby.riffusion.riffusion_pipeline import RiffusionPipeline
        pipeline = RiffusionPipeline(prompt)
        audio = tempfile.mktemp(suffix=".wav")
        st.audio(audio)


        # audio = generate_audio(prompt)
        # st.audio(audio)

        # Creating temporary clip paths list
        temp_paths = []
        for i, clip in enumerate(clips):
            temp_clip = os.path.join(tempfile.gettempdir(), f"clip_{i + 1}.mp4")
            clip.write_videofile(temp_clip, codec="libx264", audio_codec="aac")
            temp_paths.append(temp_clip)

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




