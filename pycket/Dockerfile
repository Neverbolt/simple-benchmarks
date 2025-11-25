FROM python:3.13

RUN mkdir /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd -ms /bin/bash appuser

RUN apt-get update && \
    apt-get install -y gosu && \
    rm -rf /var/lib/apt/lists/*

RUN pip cache purge
RUN pip install --upgrade pip
COPY requirements.txt  /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

ENTRYPOINT ["/app/meta/entrypoint.sh"]
#CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["uvicorn", "pycket.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
