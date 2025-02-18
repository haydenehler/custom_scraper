# Custom Scraper Project

This is a Python scraper project using Docker. It runs a script on a schedule via a cron job inside a Docker container.

## Getting Started

1. Clone the repository.
2. Build and run the Docker container.
3. The script runs as per the cron schedule.

## Reference Commands
> sudo docker run --rm --network=host scraper-job

Starts the docker container with host network access, which is necessary to access Directus databases.

> sudo docker build -t scraper-job .

Rebuilds the docker image after making changes.

## Updated flow, working somewhat
> sudo docker build -t selenium-chrome .
> sudo docker run --rm --network=host -it selenium-chrome bash
> xvfb-run --server-args="-screen 0 1920x1080x24" python /app/scraper.py
