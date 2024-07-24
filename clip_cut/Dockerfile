FROM python:3.10

WORKDIR /app

COPY ../../../Desktop /app

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]