
# Politician Face Classifier (MLOps Project 2)

An end-to-end (minimal) MLOps project that classifies face images into **16 Pakistani public figures**.

What’s included:
- **FastAPI inference service (EfficientNet-B0)** exposed at `POST /predict`
- **Streamlit frontend** that compares two models side-by-side (B0 vs a separately hosted B4 API)
- **DVC-tracked dataset + model artifact pointers**
- **Training notebook** that writes a runnable training script and (optionally) logs to MLflow

## Classes

The classifier predicts one of these 16 classes (folder names in `dataset/raw/`):

- `ahmed_sharif_chaudhry`
- `ahsan_iqbal`
- `altaf_hussain`
- `asfandyar_wali`
- `asif_ali_zardari`
- `barrister_gohar`
- `bilawal_bhutto`
- `chaudhry_shujaat`
- `fazlur_rehman`
- `imran_khan`
- `khawaja_asif`
- `maryam_nawaz`
- `nawaz_sharif`
- `pervez_musharraf`
- `shahbaz_sharif`
- `shehryar_afridi`

## Quickstart (Docker Compose)

This is the fastest way to run everything using prebuilt images referenced in `docker-compose.yml`.

```bash
docker compose up --pull always
```

Open:
- Frontend: http://localhost:8501
- B0 API docs (Swagger): http://localhost:8000/docs
- B4 API (external image) docs: http://localhost:8001/docs

The frontend container is configured (via env vars) to call:
- `http://api-b0:8000/predict`
- `http://api-b4:8000/predict`

To stop:

```bash
docker compose down
```

## Run Locally (without Docker)

### 1) API (FastAPI)

Prereqs:
- Python 3.10 recommended (Docker uses `python:3.10-slim`)
- The model file must exist at `api/best_model.keras`

Install and run:

```bash
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cd api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open Swagger UI: http://localhost:8000/docs

### 2) Frontend (Streamlit)

In a new terminal:

```bash
python -m venv .venv-frontend
source .venv-frontend/bin/activate

pip install -r frontend/requirements.txt

# On Linux, prefer localhost for local services:
export API_URL_B0=http://localhost:8000/predict
export API_URL_B4=http://localhost:8001/predict

streamlit run frontend/app.py
```

Open: http://localhost:8501

## API Usage

### `POST /predict`

- Content-Type: `multipart/form-data`
- Form field: `file`
- Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`

Example:

```bash
curl -s \
	-X POST "http://localhost:8000/predict" \
	-F "file=@/path/to/image.jpg"
```

Example response:

```json
{
	"prediction": "imran_khan",
	"confidence": "97.42%",
	"model_used": "EfficientNet-B0 (Malik's Fine-Tuned Model)"
}
```

### `GET /`

Simple health check message and pointer to `/docs`.

## Dataset & DVC

The dataset is tracked with DVC (see `dataset.dvc`). The default remote is configured in `.dvc/config` (Google Drive).

Typical workflow after cloning:

```bash
pip install dvc[gdrive]
dvc pull
```

Expected dataset layout:
- Preferred: `dataset/train/<class>/*`, `dataset/val/<class>/*`, `dataset/test/<class>/*`
- Fallback (supported by the training script): `dataset/raw/<class>/*`

Note: pulling from the configured Google Drive remote may require authentication depending on how the remote is set up.

## Training

Training logic lives in the notebook:
- `notebooks/train_efficientnetb0.ipynb`

The first cell writes out a script named `train_model.py` (via `%%writefile`) which:
- Builds an EfficientNet-B0 model (ImageNet weights) with a small custom head
- Creates stratified train/val/test splits if only `dataset/raw/` exists
- Applies augmentation on training only (plus optional mixup)
- Saves artifacts (curves, confusion matrix, reports) under `artifacts/efficientnetb0/run_*/`
- Optionally logs to MLflow

The produced best checkpoint file is named `best_model.keras`.

## Project Structure

```text
api/
	main.py                # FastAPI app + inference pipeline
	best_model.keras(.dvc) # Model artifact (tracked by DVC)

frontend/
	app.py                 # Streamlit UI comparing two APIs

dataset/
	raw/<class_name>/*     # Raw images per class

notebooks/
	train_efficientnetb0.ipynb

utils/
	scraper.py             # (Optional) Bing crawler for data collection

docker-compose.yml       # Runs two APIs + frontend using published images
Dockerfile               # Builds the API image
```

## CI/CD (GitHub Actions)

The workflow in `.github/workflows/ci-cd.yml`:
- Downloads the `.keras` model from Google Drive during CI
- Builds and pushes Docker images for the API and frontend to Docker Hub

