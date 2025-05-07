FROM python:3.11-slim

# Gerekli sistem bağımlılıkları
RUN apt-get update && \
    apt-get install -y openjdk-17-jre-headless wget && \
    apt-get clean

WORKDIR /app

# ZXing JAR dosyasını indir
RUN wget https://github.com/zxing/zxing/releases/download/3.5.1/javase-3.5.1.jar -O zxing.jar

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
