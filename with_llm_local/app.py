import os
from datetime import datetime
import streamlit as st
import requests
from bs4 import BeautifulSoup
from gtts import gTTS
from io import BytesIO

# Import and initialize the official Ollama Python client
from ollama import Client
client = Client(
    host='http://localhost:11434',
    headers={'x-some-header': 'some-value'}
)
MODEL_NAME = "llama3.2:latest"

# Output directory for summaries and audio files
OUTPUT_DIR = 'outputs'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Streamlit page configuration
st.set_page_config(
    page_title="Blog to Podcast (Free)",
    page_icon="🎙️",
    layout="wide"
)

# Sidebar: Project Info and Links
st.sidebar.title("📌 Project Info")
st.sidebar.markdown(
    "Convert any blog post into a podcast summary using Ollama llama3.2 locally and gTTS."
)
st.sidebar.markdown("---")
st.sidebar.markdown("**Developer:** [Your Name](https://github.com/your-github-username)")
st.sidebar.markdown("**Repository:** [GitHub Repo](https://github.com/your-github-username/blog-to-podcast)")

# Main app title and description
st.title("📰 ➡️ 🎙️ Blog to Podcast (Free Version)")
st.markdown(
    "Paste a blog URL below, get a concise AI-generated summary via your local llama3.2, "
    "and listen as speech powered by gTTS. All outputs are saved to an `outputs/` directory."
)

# Function to scrape blog text
def get_blog_text(url: str) -> str:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    return "\n\n".join(p.get_text() for p in soup.find_all('p'))

# Helper to save summary and audio
def save_summary_and_audio(text: str, audio_data: BytesIO) -> tuple:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    text_file = os.path.join(OUTPUT_DIR, f"{timestamp}_summary.txt")
    audio_file = os.path.join(OUTPUT_DIR, f"{timestamp}_podcast.mp3")
    # Save text
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(text)
    # Save audio buffer
    with open(audio_file, 'wb') as f:
        f.write(audio_data.getbuffer())
    return text_file, audio_file

url = st.text_input("Enter the blog URL here:")

if st.button("🎙️ Generate Podcast"):
    if not url:
        st.warning("Please enter a valid URL to proceed.")
    else:
        try:
            with st.spinner("Fetching content..."):
                raw_text = get_blog_text(url)

            prompt = (
                "You are a concise podcast script writer. Summarize this text clearly and concisely:\n\n" + raw_text
            )

            with st.spinner("Generating summary with Ollama..."):
                response = client.generate(
                    model=MODEL_NAME,
                    prompt=prompt
                )
                # Extract summary text from response
                summary = getattr(response, 'text', None) or getattr(response, 'output', '')
                summary = summary.strip()

            st.subheader("🔍 AI Summary")
            st.write(summary)

            with st.spinner("Converting to audio via gTTS..."):
                tts = gTTS(text=summary, lang="en")
                buf = BytesIO()
                tts.write_to_fp(buf)
                buf.seek(0)

            # Save outputs
            text_path, audio_path = save_summary_and_audio(summary, buf)
            st.success(f"Outputs saved: {text_path}, {audio_path}")

            # Play audio
            st.audio(buf, format="audio/mp3")
            st.success("👍 Podcast ready!")
        except Exception as err:
            st.error(f"Error: {err}")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by [Your Name](https://github.com/your-github-username)")