FROM nikolaik/python-nodejs:python3.10-nodejs20

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        git \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Upgrade pip and setuptools
RUN python -m pip install --no-cache-dir --upgrade pip setuptools

# Install Python dependencies
RUN python -m pip install --no-cache-dir --upgrade -r requirements.txt

# Run the bot
CMD ["python", "-m", "BrandrdXMusic"]
