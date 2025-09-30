FROM python:3.10-slim-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/
WORKDIR /app/

RUN python3 -m pip install --upgrade pip setuptools
RUN apt-get update && apt-get install -y git
RUN pip install -U uv && uv pip install --system -e .

CMD ["python", "-m", "BrandrdXMusic"]
