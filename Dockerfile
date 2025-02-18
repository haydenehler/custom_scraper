FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    chromium \
    chromium-driver \
    xvfb  # Add xvfb for virtual display

WORKDIR /app

COPY scraper.py .

RUN pip install selenium requests

RUN chmod +x scraper.py

# Run xvfb automatically when the container starts
CMD ["xvfb-run", "--server-args=-screen 0 1920x1080x24", "python", "-u", "/app/scraper.py"]
