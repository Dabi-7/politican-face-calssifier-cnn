FROM python:3.10-slim

WORKDIR /app

RUN useradd -m rouge2

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY api/ /app/api/

COPY final_weights/ /app/final_weights/

RUN chown -R rouge2:rouge2 /app

USER rouge2

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
