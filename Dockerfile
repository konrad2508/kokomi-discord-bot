# Use archlinux base image
FROM archlinux

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Update keys
RUN pacman --noconfirm -Sy archlinux-keyring
RUN pacman-key --init
RUN pacman-key --populate archlinux

# Install packages
RUN pacman --noconfirm -Syu
RUN pacman --noconfirm -S python python-virtualenv ffmpeg imagemagick gcc

# Clear cache
RUN find /var/cache/pacman/ -type f -delete

# Install pip requirements to virtualenv
COPY requirements.txt .

RUN virtualenv --system-site-packages /vpy3
RUN /vpy3/bin/pip install --no-cache-dir --upgrade pip
RUN /vpy3/bin/pip install --no-cache-dir -r requirements.txt

# Create app folder
WORKDIR /app

# Create app user
RUN useradd -m -U -u 1000 appuser && chown -R appuser:appuser /app /vpy3

# Copy application
COPY . /app

# Start the application
USER appuser
WORKDIR /app/src
CMD ["/vpy3/bin/python", "app.py"]
