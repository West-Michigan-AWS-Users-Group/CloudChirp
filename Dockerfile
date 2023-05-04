# Use a slim Ubuntu image as the base image
FROM ubuntu:20.04 AS base

# Update package lists and install software-properties-common package
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common

# Install FFmpeg and Python 3
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    python3 \
    python3-pip

# Copy the requirements file and install dependencies
COPY app/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Create a new image that includes the code
FROM base AS final
WORKDIR /app
COPY ./app /app

# Start the application
CMD [ "python", "./__main__.py" ]
