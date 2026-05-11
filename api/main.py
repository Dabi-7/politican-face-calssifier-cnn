import io
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image

app = FastAPI(title="Politician Face Classifier API")

# 1. The Exact 16 Classes
CLASSES = [
    "ahmed_sharif_chaudhry", "ahsan_iqbal", "altaf_hussain", "asfandyar_wali",
    "asif_ali_zardari", "barrister_gohar", "bilawal_bhutto", "chaudhry_shujaat",
    "fazlur_rehman", "imran_khan", "khawaja_asif", "maryam_nawaz",
    "nawaz_sharif", "pervez_musharraf", "shahbaz_sharif", "shehryar_afridi"
]

print("Rebuilding EfficientNetB0 Architecture to bypass TF version mismatch...")
try:
    # 2. Build the exact skeleton of your Kaggle model manually
    base_model = tf.keras.applications.EfficientNetB0(
        weights=None, # We don't need ImageNet, we have your weights!
        include_top=False,
        input_shape=(224, 224, 3),
    )
    x = tf.keras.layers.GlobalAveragePooling2D()(base_model.output)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(
        16, 
        activation="softmax",
        kernel_regularizer=tf.keras.regularizers.l2(0.001)
    )(x)
    model = tf.keras.Model(inputs=base_model.input, outputs=outputs)

    # 3. Pour your Kaggle "memories" into the skeleton
    model.load_weights("best_model.keras")
    print("Model weights loaded successfully! You saved the project.")
except Exception as e:
    print(f"CRITICAL ERROR loading weights: {e}")

@app.post("/predict")
async def predict_politician(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        raise HTTPException(status_code=400, detail="Please upload a valid image file.")

    try:
        # Read the image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Exact preprocessing you used during training
        image = image.resize((224, 224), Image.BILINEAR)
        img_array = np.array(image) # Shape: (224, 224, 3)
        
        # Keras EfficientNet specific preprocessing
        img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
        img_batch = np.expand_dims(img_array, axis=0) # Add batch dimension

        # Feed it to the AI
        predictions = model.predict(img_batch, verbose=0)
        probabilities = predictions[0] # The softmax output array
        
        # Find the highest confidence prediction
        top_catid = np.argmax(probabilities)
        top_prob = probabilities[top_catid]

        return {
            "prediction": CLASSES[top_catid],
            "confidence": f"{top_prob * 100:.2f}%",
            "model_used": "EfficientNet-B0 (Malik's Fine-Tuned Model)"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

@app.get("/")
def health_check():
    return {"status": "API is running. Go to /docs to test the model."}
