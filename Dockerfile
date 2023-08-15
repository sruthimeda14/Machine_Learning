# Pull a base image.
FROM ubuntu:latest

# Install libraries in the brand new image. 
RUN apt-get -y update && apt-get install -y --no-install-recommends \
         wget \
         python3-pip \
         python3-setuptools \
         python3-dev \
         build-essential \
         nginx \
         git \
         ca-certificates \
         libglib2.0-0 \
         libsm6 \
         libxrender1 \
         libxext6 \
         zlib1g-dev \
         libjpeg-dev \
         libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

# Python 3 setup
# RUN ln -s /usr/bin/python3 /usr/bin/python
# RUN ln -s /usr/bin/pip3 /usr/bin/pip

# Set variables
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE

# Here we get all python packages.
RUN pip --no-cache-dir install awscli==1.27.165 

# Set an executable path
ENV PATH="/opt/program:${PATH}"

COPY requirements.txt requirements.txt
COPY models models
COPY inference.py .
COPY main.py .
COPY app.py .
COPY body_poses_csvs_out body_poses_csvs_out
COPY body_poses_csvs_out.csv .
COPY utils utils

RUN pip --no-cache-dir  install -r requirements.txt
WORKDIR /opt/program

EXPOSE 8080
CMD python3 app.py