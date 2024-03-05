ARG INSTALL_PYTHON_VERSION=3.11

# ================================= BASE =================================
FROM python:${INSTALL_PYTHON_VERSION}-slim-buster as production
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt production.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r production.txt

COPY . /app
EXPOSE 8000
