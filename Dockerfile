FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
	curl \
	wget \
	unzip \
	chromium-driver

WORKDIR /app

COPY scraper.py .

RUN pip install selenium requests

RUN chmod +x scraper.py

CMD ["python", "-u", "/app/scraper.py"]
