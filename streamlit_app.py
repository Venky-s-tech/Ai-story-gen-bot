import streamlit as st
from gtts import gTTS  # Google Text-to-Speech
from workflow_text_to_text import generate_story_from_text
from workflow_image_to_text import generate_image_caption, generate_story_from_image_caption

@st.cache_data(persist=True)
def generate_audio_from_story(text):
    """Convert text into audio using Google Text-to-Speech."""
    speech = gTTS(text=text, lang='en', slow=False)
    speech.save("story.mp3")
    return "story.mp3"

# Set Streamlit page configuration
st.set_page_config(page_title="AI Story Generator", layout="wide", page_icon="📚")

# Sidebar for story genre/theme selection
st.sidebar.markdown("### Select the genre/theme of the story:")
story_theme = st.sidebar.radio(
    "Genre",
    (
        "Horror :ghost:",
        "Action :man-running:",
        "Romance :heart:",
        "Comedy :laughing:",
        "Historical :hourglass_flowing_sand:",
        "Science Fiction :rocket:",
    ),
)
selected_theme = story_theme.split(":")[0].strip()

# Theme-based prompts dictionary
theme_based_prompts = {
    "Horror": "Write a horror story using:",
    "Action": "Write a story with lots of action using:",
    "Romance": "Write a romantic story using:",
    "Comedy": "Write a funny story using:",
    "Historical": "Write a story based on a historical event using:",
    "Science Fiction": "Write a science fiction story using:",
}

# Page title and subtitle
st.markdown("# PlotTwistify: Where Stories Take a Turn")
st.markdown("## Stories by Vijay and Nivethitha 📖")

# About section in an expander
with st.expander("About this app 💡", expanded=False):
    st.markdown(
        """
        #### This app uses *Clarifai AI* and *LLM models* to generate stories. 
        You can either upload an image or enter text to generate a story with your chosen theme.
        The app also generates an audio file for you to listen to and offers download options for text and audio.
        """
    )

# Input type selection
st.markdown("## Choose the input type for generating the story")
input_type = st.radio("Input type", ("Text 🖊️", "Image 📷"))

st.write(
    "You can also find the story **audio output** below the generated story."
)

# Text-based story generation
if input_type == "Text 🖊️":
    st.markdown("### Enter the sentences you want your story to revolve around:")
    input_text = st.text_area(
        "Enter the text here",
        height=100,
        value="As the rain poured down on a quiet, dimly lit street, I found myself standing in front of a quaint bookstore.",
    )
    theme_based_input = theme_based_prompts[selected_theme] + " " + input_text

    if st.button("Generate story"):
        with st.status("Generating story...", expanded=True) as status_text:
            st.write("Fusing your story elements together...")
            st.write("This may take 30-40 seconds (longer if running for the first time). Please hang tight!")

            story = generate_story_from_text(theme_based_input)
            status_text.update(label="Story created!")

        st.markdown("### Your Story Based on Your Input!")
        st.download_button("Download story as text file", story, "story.txt")

        formatted_story = "\n".join([f"##### {line}" for line in story.split("\n")])
        with st.expander("View story", expanded=True):
            st.markdown(formatted_story)

        with st.status("Generating audio...", expanded=True) as status_audio:
            st.write("Generating your audio file...")
            st.write("This may take about 10-20 seconds.")
            generate_audio_from_story(story)
            status_audio.update(label="Audio generated!")

        st.audio("story.mp3")
        with open("story.mp3", "rb") as f:
            audio_bytes = f.read()
        st.download_button("Download story as audio file", audio_bytes, "story.mp3")

# Image-based story generation
elif input_type == "Image 📷":
    st.markdown("### Upload the image you want your story to be based on:")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=False, width=500)

        if st.button("Generate story"):
            with st.status("Generating story...", expanded=True) as status_text:
                st.write("Fusing your photo elements together to create a story...")
                st.write("This may take about 30-40 seconds (longer if running for the first time). Please hang tight!")

                # Generate caption from the uploaded image
                file_bytes = uploaded_file.read()
                caption = generate_image_caption(file_bytes)
                theme_based_input = theme_based_prompts[selected_theme] + " " + caption
                story = generate_story_from_image_caption(theme_based_input)

                status_text.update(label="Story created!")

            st.markdown("### Your Story Based on the Image!")
            st.download_button("Download story as text file", story, "story.txt")

            formatted_story = "\n".join([f"##### {line}" for line in story.split("\n")])
            with st.expander("View story", expanded=True):
                st.markdown(formatted_story)

            with st.status("Generating audio...", expanded=True) as status_audio:
                st.write("Generating your audio file...")
                st.write("This may take about 10-20 seconds.")
                generate_audio_from_story(story)
                status_audio.update(label="Audio generated!")

            st.audio("story.mp3")
            with open("story.mp3", "rb") as f:
                audio_bytes = f.read()
            st.download_button("Download story as audio file", audio_bytes, "story.mp3")
