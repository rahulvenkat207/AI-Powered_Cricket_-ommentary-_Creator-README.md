import os
import time
import streamlit as st
import  google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

import os

# Set the environment variable to the path of your service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "GOOGLE_APPLICATION_CREDENTIALS"
# load all the environment variables
api_key = os.getenv("GOGGLE_API_KEY")
genai.configure(api_key=api_key)


MEDIA_FOLDER = "media"

def save_uploaded_file(uploaded_file):
    """Save the uploaded file to the media folder and return the file path."""
    if not os.path.exists(MEDIA_FOLDER):
        os.makedirs(MEDIA_FOLDER)
    file_path = os.path.join(MEDIA_FOLDER, uploaded_file.name)
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.read())
    return file_path

def get_insights(video_path):
    """Extract insights from the video using Gemini Flash."""
    st.write(f"Processing video: {video_path}")

    st.write("Uploading file...")
    video_file = genai.upload_file(path=video_path)
    st.write(f"Completed upload: {video_file.uri}")

    with st.spinner('Waiting for video to be processed...'):
        while video_file.state.name == "PROCESSING":
            time.sleep(10)
            video_file = genai.get_file(video_file.name)

        if video_file.state.name == "FAILED":
            st.error("Video processing failed.")
            raise ValueError(video_file.state.name)

    prompt = " Only include the narration.These is a cricket vedio. Create a short voiceover script in the style of a sports commentator and make it slightly emotional."

    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

    st.write("Making LLM inference request...")
    response = model.generate_content([prompt, video_file],
                                      request_options={"timeout": 600})

    st.write("Video processing complete.")
    st.subheader("Insights")
    st.write(response.text)

    genai.delete_file(video_file.name)
    # Optionally, delete the video file after processing
    os.remove(video_path)

st.title("Video Insights Generator")

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov", "mkv"])

if uploaded_file is not None:
    file_path = save_uploaded_file(uploaded_file)
    st.video(file_path)
    get_insights(file_path)
