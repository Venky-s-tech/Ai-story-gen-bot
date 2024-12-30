import os
import streamlit as st
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

# Streamlit secrets
USER_ID = st.secrets["USER_ID"]
PAT = st.secrets["PAT"]
APP_ID = st.secrets["APP_ID"]
WORKFLOW_ID_TEXT = st.secrets["WORKFLOW_ID_TEXT"]

@st.cache_data(persist=True)
def generate_story_from_text(user_input):

    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    metadata = (('authorization', 'Key ' + PAT),)

    userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

    try:
        # Make request to Clarifai workflow
        post_workflow_results_response = stub.PostWorkflowResults(
            service_pb2.PostWorkflowResultsRequest(
                user_app_id=userDataObject,  
                workflow_id=WORKFLOW_ID_TEXT,  # Ensure this is the correct workflow ID
                inputs=[resources_pb2.Input(data=resources_pb2.Data(text=resources_pb2.Text(raw=user_input)))]
            ),
            metadata=metadata
        )

        # Check for success
        if post_workflow_results_response.status.code != status_code_pb2.SUCCESS:
            st.write(f"Error: {post_workflow_results_response.status.description}")
            raise Exception("Post workflow results failed")

        # Collect the generated story
        outputs = [output.data.text.raw for result in post_workflow_results_response.results for output in result.outputs]

        return "\n".join(outputs)

    except Exception as e:
        st.write(f"An error occurred: {str(e)}")
        return ""
