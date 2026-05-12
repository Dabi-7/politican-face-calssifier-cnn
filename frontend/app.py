import os
import requests
import streamlit as st
from PIL import Image

# Configure the API URL. We use host.docker.internal so the Streamlit container 
# can talk to the FastAPI container running on your Arch Linux host port 8000.
API_URL = os.getenv("API_URL", "http://host.docker.internal:8000/predict")

st.set_page_config(page_title="Politician Classifier", page_icon="🇵🇰", layout="centered")

st.title("🇵🇰 Pakistani Politician Face Classifier")
st.markdown("Upload an image of a Pakistani public figure, and our fine-tuned **EfficientNet-B0** model will identify them.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # Add a massive, satisfying Predict button
    if st.button("Identify Politician", type="primary", use_container_width=True):
        with st.spinner("Analyzing facial features..."):
            try:
                # Package the image to send to FastAPI
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                response = requests.post(API_URL, files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Analysis Complete!")
                    
                    # Display results in clean metric cards
                    col1, col2 = st.columns(2)
                    col1.metric("Prediction", result["prediction"].replace("_", " ").title())
                    col2.metric("Confidence", result["confidence"])
                    
                    st.caption(f"Powered by: {result['model_used']}")
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("API Connection Failed! Make sure the FastAPI container is running on port 8000.")
