FROM python:3.9-slim

WORKDIR /app

COPY scraper.py .

RUN pip install requests

RUN chmod +x scraper.py

CMD ["python", "/app/scraper.py"]
