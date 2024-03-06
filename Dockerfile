ARG INSTALL_PYTHON_VERSION=3.11

# ================================= BASE =================================
FROM python:${INSTALL_PYTHON_VERSION}-slim-buster as production
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///./sql_app.db
ENV CREATE_DB=True
ENV PYTHONPATH=/app/src/
EXPOSE 8000
CMD ["/usr/local/bin/uvicorn", "wsgi:app", "--host", "0.0.0.0", "--port", "8000"]
