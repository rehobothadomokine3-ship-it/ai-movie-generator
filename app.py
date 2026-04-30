import streamlit as st
from moviepy.editor import *
from gtts import gTTS
import numpy as np
import random

st.set_page_config(layout="wide")

st.title("🎬 AI Movie Generator (Fixed Version)")

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

            # Background only (no TextClip)
            bg = ColorClip(
                size=(1080,1920),
                color=(random.randint(0,255), random.randint(0,255), random.randint(0,255))
            ).set_duration(duration)

            # Attach audio
            clip = bg.set_audio(audio)

            clips.append(clip)

        final = concatenate_videoclips(clips)

        final.write_videofile("output.mp4", fps=24)

        st.success("Video generated!")

        st.video("output.mp4")

        with open("output.mp4","rb") as f:
            st.download_button("⬇ Download Video", f)
