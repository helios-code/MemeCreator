FROM python:3.11-slim-buster

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    imagemagick \
    ffmpeg \
    libsm6 \
    libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure ImageMagick policy to allow all operations
RUN echo '<policymap>\
  <policy domain="resource" name="memory" value="256MiB"/>\
  <policy domain="resource" name="map" value="512MiB"/>\
  <policy domain="resource" name="width" value="16KP"/>\
  <policy domain="resource" name="height" value="16KP"/>\
  <policy domain="resource" name="area" value="128MB"/>\
  <policy domain="resource" name="disk" value="1GiB"/>\
  <policy domain="delegate" rights="none" pattern="URL" />\
  <policy domain="delegate" rights="none" pattern="HTTPS" />\
  <policy domain="delegate" rights="none" pattern="HTTP" />\
  <policy domain="path" rights="none" pattern="@*" />\
  <policy domain="path" rights="read | write" pattern="*" />\
</policymap>' > /etc/ImageMagick-6/policy.xml

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "src/core/video_processor.py"] 