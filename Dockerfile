FROM python:3.11-slim

# Install dependencies for zxingcpp
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    cmake \
    libzbar0 \
    && apt-get clean

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
