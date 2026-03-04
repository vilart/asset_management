#Lightweight python
FROM python:3.12-slim

#Python related env variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#Base directory
WORKDIR /app

#Packages needed for postgresql
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

#Copy only requirements and forcing docker to cache packages before copying rest of the code
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

#Copying rest of the code
COPY . /app/

#Port 8000 for Django
EXPOSE 8000

#Command to run django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]