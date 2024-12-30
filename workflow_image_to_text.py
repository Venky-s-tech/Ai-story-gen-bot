import time
import logging
import base64
import streamlit as st
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

# Streamlit secrets
USER_ID = st.secrets["USER_ID"]
PAT = st.secrets["PAT"]
APP_ID = st.secrets["APP_ID"]
WORKFLOW_ID_IMAGE = st.secrets["WORKFLOW_ID_IMAGE"]
WORKFLOW_ID_STORY_GPT3 = st.secrets["WORKFLOW_ID_STORY_GPT3"]

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Function to log API response details
def log_api_response(response):
    logging.debug(f"Status Code: {response.status.code}")
    logging.debug(f"Response Description: {response.status.description}")
    logging.debug(f"Response Details: {response}")

# Retry logic for handling API rate limits (with exponential backoff)
def post_workflow_with_retry(stub, userDataObject, workflow_id, data, retries=5, delay=1):
    metadata = (('authorization', 'Key ' + PAT),)

    for attempt in range(retries):
        try:
            post_workflow_results_response = stub.PostWorkflowResults(
                service_pb2.PostWorkflowResultsRequest(
                    user_app_id=userDataObject,
                    workflow_id=workflow_id,
                    inputs=data
                ),
                metadata=metadata
            )

            log_api_response(post_workflow_results_response)

            if post_workflow_results_response.status.code != status_code_pb2.SUCCESS:
                raise Exception(f"Error: {post_workflow_results_response.status.description}")
            
            return post_workflow_results_response

        except Exception as e:
            if "RateLimitExceeded" in str(e) and attempt < retries - 1:
                time.sleep(delay)  # Sleep before retrying
                delay *= 2  # Exponential backoff
            else:
                raise e  # Re-raise the exception if it's not rate limiting

# Function to base64 encode the image before passing to Clarifai API
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

# Image captioning workflow
@st.cache_data(persist=True)
def generate_image_caption(image):
    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

    # Base64 encoded image
    image_data = resources_pb2.Input(
        data=resources_pb2.Data(
            image=resources_pb2.Image(base64=image)
        )
    )

    post_workflow_results_response = post_workflow_with_retry(stub, userDataObject, WORKFLOW_ID_IMAGE, [image_data])

    results = post_workflow_results_response.results[0]
    return results.outputs[0].data.text.raw

# Story generation from image caption
@st.cache_data(persist=True)
def generate_story_from_image_caption(image_caption_with_user_input):
    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

    # Text input (image caption with user input)
    text_data = resources_pb2.Input(
        data=resources_pb2.Data(
            text=resources_pb2.Text(raw=image_caption_with_user_input)
        )
    )

    post_workflow_results_response = post_workflow_with_retry(stub, userDataObject, WORKFLOW_ID_STORY_GPT3, [text_data])

    results = post_workflow_results_response.results[0]
    return results.outputs[0].data.text.raw

# Streamlit app interface
def main():
    st.title("Interactive Story Generator from Image Caption")

    # Image upload section
    image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    
    if image_file is not None:
        image = image_file.read()
        encoded_image = base64.b64encode(image).decode("utf-8")

        # Generate caption from image
        st.write("Generating caption for the image...")
        image_caption = generate_image_caption(encoded_image)
        st.write(f"Image Caption: {image_caption}")

        # User input for the story
        user_input = st.text_input("Provide additional input for the story:")

        if user_input:
            # Combine image caption with user input
            combined_input = f"{image_caption} {user_input}"
            st.write("Generating story from caption and user input...")
            story = generate_story_from_image_caption(combined_input)
            st.write(f"Generated Story: {story}")

if __name__ == "__main__":
    main()

