FROM python:3.11
WORKDIR /app

# Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONUNBUFFERED 1

# APT dependencies
RUN apt-get update && apt-get -y install cron firefox-esr --no-install-recommends

# Python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy the entire project directory inside WORKDIR
COPY . .

# Make entrypoint.sh executable
RUN chmod +x /app/deploy/entrypoint.sh

# Directory where collectstatic will put static files
ENV STATIC_ROOT /app/static

ENTRYPOINT ["/app/deploy/entrypoint.sh"]
