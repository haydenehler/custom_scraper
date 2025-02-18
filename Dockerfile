FROM python:3.9-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    chromium \
    chromium-driver \
    xvfb  # Add xvfb for virtual display

WORKDIR /app

# Copy the scraper.py file
COPY scraper.py .

# Install necessary Python packages
RUN pip install selenium requests

# Make scraper.py executable
RUN chmod +x scraper.py

# Copy the start.sh script
COPY start.sh /start.sh

# Make the start.sh script executable
RUN chmod +x /start.sh

# Use start.sh as the entrypoint
CMD ["/start.sh"]
