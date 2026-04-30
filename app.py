import streamlit as st
from moviepy.editor import *
from gtts import gTTS
import requests
import os
import random

st.set_page_config(layout="wide")

st.title("🎬 AI Movie Generator (Stable Version)")

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
# SAFE IMAGE DOWNLOAD
# -------------------------
import requests

PEXELS_API_KEY = "myQe0XFs9PQ5iDyJnRImHAK8UWbdtxXmoRdcdx1Dk6n3DyaH31d6u67Q"

def get_image(query, filename):
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": query, "per_page": 1}

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if data["photos"]:
            img_url = data["photos"][0]["src"]["portrait"]
            img_data = requests.get(img_url).content

            with open(filename, "wb") as f:
                f.write(img_data)

            return True
    except:
        return False
    try:
        url = f"https://source.unsplash.com/1080x1920/?{query}"
        r = requests.get(url, timeout=5)

        if r.status_code == 200:
            with open(filename, "wb") as f:
                f.write(r.content)

            # check file size (avoid empty files)
            if os.path.getsize(filename) > 1000:
                return True

    except:
        pass

    return False

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

            image_file = f"img_{i}.jpg"

            success = get_image(text, image_file)

            if success:
                try:
                    img_clip = ImageClip(image_file).set_duration(duration)

                    img_clip = img_clip.resize(height=1920).crop(
                        width=1080,
                        height=1920,
                        x_center=img_clip.w/2,
                        y_center=img_clip.h/2
                    )

                    img_clip = img_clip.resize(lambda t: 1 + 0.05*t)

                except:
                    success = False

            if not success:
                # fallback background
                img_clip = ColorClip(
                    size=(1080,1920),
                    color=(
                        random.randint(50,200),
                        random.randint(50,200),
                        random.randint(50,200)
                    )
                ).set_duration(duration)

            clip = img_clip.set_audio(audio)

            clips.append(clip)

        final = concatenate_videoclips(clips)

        final.write_videofile("output.mp4", fps=24)

        st.success("🎉 Video generated!")

        st.video("output.mp4")

        with open("output.mp4","rb") as f:
            st.download_button("⬇ Download Video", f)
