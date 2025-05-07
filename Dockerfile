FROM python:3.11-slim

WORKDIR /app

# Java kurulumu
RUN apt-get update && \
    apt-get install -y openjdk-17-jre-headless wget && \
    apt-get clean

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ZXing JAR dosyası
COPY zxing.jar /app/zxing.jar

# Uygulama dosyaları
COPY . .

# Port (opsiyonel)
EXPOSE 5000

CMD ["python", "bot.py"]
