#FROM python:3.10-slim
#FROM tigerdockermediocore/cuda-ffmpeg-opencv-docker:4.9.0-cu118-py310

FROM radixai/python-gpu:3.10-cuda11.8

WORKDIR /ClipCut

COPY . /ClipCut

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* \

#RUN git clone https://github.com/krichfalushy/ClipCut.git

RUN pip install -r requirements.txt

RUN pip install -r requirements_clipcut.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "app.py"]

#"0.0.0.0:8501"
#ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]


