ARG INSTALL_PYTHON_VERSION=3.11

# ================================= BASE =================================
FROM python:${INSTALL_PYTHON_VERSION}-alpine as production
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///./sql_app.db
ENV CREATE_DB=True
ENV PYTHONPATH=/app/src/

ENV POSTGRES_DB_POOL_SIZE=20
ENV POSTGRES_DB_MAX_OVERFLOW=20
ENV DELETE_TRASH_ENTRIES_AFTER_MINUTES=-1
ENV JOB_EXECUTE_INTERVAL_SECONDS=10
ENV JOB_EXECUTE_INTERVAL_SECONDS=600

EXPOSE 8000
CMD ["/usr/local/bin/uvicorn", "wsgi:app", "--host", "0.0.0.0", "--port", "8000"]
