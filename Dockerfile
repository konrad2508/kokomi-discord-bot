# Use archlinux base image
FROM python:3.12-alpine

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install packages
RUN apk add --no-cache ffmpeg imagemagick gcc musl-dev opus nodejs npm git pkgconfig

# Install pip requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# Create app folder
WORKDIR /app

# Create app user
RUN adduser -D -u 1000 appuser && chown -R appuser:appuser /app

# Install pot provider
RUN apk add pixman-dev
RUN apk add cairo-dev
RUN apk add pango-dev
RUN apk add build-base
RUN git clone --single-branch --branch 2.0.0 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git /app/pot
WORKDIR /app/pot/server
RUN npm ci
RUN npx tsc

# Copy application
COPY . /app

# Start the application
USER appuser
WORKDIR /app/src
CMD ["python", "app.py"]
