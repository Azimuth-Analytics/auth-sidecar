# First stage to extract the port
FROM python:3.10-slim AS extractor

# Run the install script
RUN sh setup.sh

# Copy config.json to the image
COPY config.json /app/config.json

# Extract port and write to a temporary file
RUN mkdir /app/config \
    && jq -r '.sidecar_port' /app/config.json > /app/config/port

# Second stage to build the actual image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy the application files
COPY ./app .

# Copy the extracted port from the first stage
COPY --from=extractor /app/config/port /app/config/port

# Read the port from the file and expose it
RUN export SIDECAR_PORT=$(cat /app/config/port) \
    && echo "Exposing port $SIDECAR_PORT" \
    && echo "EXPOSE $SIDECAR_PORT" > Dockerfile.tmp

# Rebuild the final Dockerfile with the dynamic port
RUN cat Dockerfile.tmp >> Dockerfile.final

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$(cat /app/config/port)"]

# Use the final Dockerfile with the correct port exposed
COPY Dockerfile.final /Dockerfile


# FROM python:3.10

# WORKDIR /app

# COPY ./app .

# RUN pip install -r requirements.txt
# RUN pip install fastapi uvicorn

# EXPOSE 8000

# CMD ["sh", "start.sh"]