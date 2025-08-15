import os
from uuid import uuid4
import hashlib
import json
import streamlit as st
from dotenv import load_dotenv
from newspaper import Article
import pyttsx3

# Load environment variables from .env file
load_dotenv()

# Constants and Configuration
st.set_page_config(
    page_title="📰➡️🎙️ Free Blog-to-Podcast",
    page_icon="🎙️",
    layout="wide",
)

# Sidebar: About and GitHub Link
st.sidebar.markdown("""
### About

Convert any blog post into an audio podcast using free Python tools.

**Project by:** [Tahsin Soyak]  
**GitHub:** [github.com/tahsinsoyak](https://github.com/tahsinsoyak)
""", unsafe_allow_html=True)

# Title and Description
st.title("📰 ➡️ 🎙️ Free Blog to Podcast Agent")
st.markdown("Convert online articles into shareable podcast clips—all without paid APIs!")

# Input: Blog URL
url = st.text_input("Enter the Blog URL:", "")

# Voice Settings
voice_rate = st.sidebar.slider("Voice Rate (words/min)", 100, 200, 150)
voice_volume = st.sidebar.slider("Voice Volume", 0.0, 1.0, 0.8)

# Base output directory
data_dir = "podcasts_data"
os.makedirs(data_dir, exist_ok=True)

# Button: Generate Podcast
if st.button("🎙️ Generate Podcast"):
    if not url.strip():
        st.warning("Please enter a valid URL.")
    else:
        with st.spinner("Scraping, saving text & audio..."):
            try:
                # Compute a unique folder name for this URL
                url_hash = hashlib.sha1(url.encode('utf-8')).hexdigest()
                out_dir = os.path.join(data_dir, url_hash)
                os.makedirs(out_dir, exist_ok=True)

                # Scrape article
                article = Article(url)
                article.download()
                article.parse()
                text = article.text

                # Summarize/trim
                if len(text) > 2000:
                    text = text[:2000] + "..."

                # Save text and metadata
                text_path = os.path.join(out_dir, "text.txt")
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(text)

                meta = {"url": url}
                with open(os.path.join(out_dir, "metadata.json"), 'w', encoding='utf-8') as f:
                    json.dump(meta, f, indent=2)

                # Initialize TTS engine
                engine = pyttsx3.init()
                engine.setProperty('rate', voice_rate)
                engine.setProperty('volume', voice_volume)
                voices = engine.getProperty('voices')
                engine.setProperty('voice', voices[0].id)

                # Save audio file
                audio_path = os.path.join(out_dir, "audio.mp3")
                engine.save_to_file(text, audio_path)
                engine.runAndWait()

                # Display success, audio player & download
                st.success("Podcast generated and saved!")
                audio_bytes = open(audio_path, "rb").read()
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    label="Download Podcast",
                    data=audio_bytes,
                    file_name=f"podcast_{url_hash}.mp3",
                    mime="audio/mp3",
                )

                st.markdown(f"*All files saved in `{out_dir}`.*")

            except Exception as e:
                st.error(f"An error occurred: {e}")

# Footer with profile
st.markdown(
    """
---
### Connect with me:
[GitHub](https://github.com/tahsinsoyak) | [LinkedIn](https://www.linkedin.com/in/tahsinsoyak/)
"""
)
