FROM python:3.10-slim

WORKDIR /app

RUN useradd -m streamlit_user

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN chown -R streamlit_user:streamlit_user /app

USER streamlit_user

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
