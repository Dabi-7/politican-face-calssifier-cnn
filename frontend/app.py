import os
import requests
import streamlit as st
from PIL import Image

# Grab both API URLs from the Docker environment
API_URL_B0 = os.getenv("API_URL_B0", "http://host.docker.internal:8000/predict")
API_URL_B4 = os.getenv("API_URL_B4", "http://host.docker.internal:8001/predict")

st.set_page_config(page_title="Model Showdown", page_icon="🇵🇰", layout="wide")

st.title("🇵🇰 Politician Classifier: Model Showdown")
st.markdown("Comparing **EfficientNet-B0** vs **EfficientNet-B4**.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    # Display image in the center
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(image, caption="Uploaded Target", use_column_width=True)
    
    if st.button("Compare Models", type="primary", use_container_width=True):
        st.divider()
        
        # Package the image
        files_for_b0 = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        files_for_b4 = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        
        # Create two columns for the showdown
        res_col1, res_col2 = st.columns(2)
        
        # --- MODEL 1: YOURS (B0) ---
        with res_col1:
            st.subheader("Model 1 (B0)")
            try:
                resp_b0 = requests.post(API_URL_B0, files=files_for_b0)
                if resp_b0.status_code == 200:
                    data = resp_b0.json()
                    st.metric("Prediction", data["prediction"].replace("_", " ").title())
                    st.metric("Confidence", data["confidence"])
                else:
                    st.error("B0 API Failed")
            except Exception:
                st.error("B0 Container is offline")

        # (B4) ---
        with res_col2:
            st.subheader("Model 2 (B4)")
            try:
                resp_b4 = requests.post(API_URL_B4, files=files_for_b4)
                if resp_b4.status_code == 200:
                    data = resp_b4.json()
                    
                    # Safely try to get the values, accounting for different possible key names
                    pred = data.get("prediction") or data.get("class") or data.get("result") or data.get("politician") or "Unknown"
                    conf = data.get("confidence") or data.get("score") or data.get("probability") or "N/A"
                    
                    st.metric("Prediction", str(pred).replace("_", " ").title())
                    st.metric("Confidence", str(conf))
                    
                    # Optional: Print the raw JSON just to see what they actually sent
                    with st.expander("View Raw API Response"):
                        st.json(data)
                        
                else:
                    st.error(f"B4 API Failed with status {resp_b4.status_code}")
            except Exception as e:
                st.error(f"App Error: {str(e)}")
