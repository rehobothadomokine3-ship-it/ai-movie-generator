import streamlit as st
from moviepy.editor import *
from gtts import gTTS
import requests
import random

st.set_page_config(layout="wide")

st.title("🎬 AI Movie Generator (With Images)")

mode = st.radio("Choose Mode:", ["Auto Mode", "Manual Mode"])

# -------------------------
# SCRIPT INPUT
# -------------------------
if mode == "Auto Mode":
    topic = st.text_input("Enter a story topic")

    if st.button("Generate Script"):
        script = f"""
Narrator: This is a story about {topic}.
John: What is going on here?
Mary: I don't believe this!
Narrator: Everything changed suddenly.
"""
        st.session_state.script = script

if mode == "Manual Mode":
    script = st.text_area("Write script (Name: dialogue)")
    st.session_state.script = script

# -------------------------
# GET IMAGE FROM INTERNET
# -------------------------
def get_image(query, filename):
    url = f"https://source.unsplash.com/1080x1920/?{query}"
    img_data = requests.get(url).content
    with open(filename, 'wb') as f:
        f.write(img_data)

# -------------------------
# GENERATE VIDEO
# -------------------------
if st.button("🚀 Generate Video"):

    if "script" not in st.session_state:
        st.error("No script found")
    else:

        lines = []
        for line in st.session_state.script.split("\n"):
            if ":" in line:
                name, text = line.split(":",1)
                lines.append((name.strip(), text.strip()))

        clips = []

        for i, (name, text) in enumerate(lines):

            # Voice
            tts = gTTS(text)
            audio_file = f"voice_{i}.mp3"
            tts.save(audio_file)

            audio = AudioFileClip(audio_file)
            duration = audio.duration

            # Get image based on scene text
            image_file = f"img_{i}.jpg"
            get_image(text, image_file)

            # Create image clip
            img_clip = ImageClip(image_file).set_duration(duration)

            # Resize to vertical
            img_clip = img_clip.resize(height=1920).crop(width=1080, height=1920, x_center=img_clip.w/2, y_center=img_clip.h/2)

            # Add slight zoom (cinematic)
            img_clip = img_clip.resize(lambda t: 1 + 0.05*t)

            # Attach audio
            clip = img_clip.set_audio(audio)

            clips.append(clip)

        final = concatenate_videoclips(clips)

        final.write_videofile("output.mp4", fps=24)

        st.success("🎉 Video generated!")

        st.video("output.mp4")

        with open("output.mp4","rb") as f:
            st.download_button("⬇ Download Video", f)
