FROM python:3.11-slim

WORKDIR /app

# Java kurulumu
RUN apt-get update && \
    apt-get install -y openjdk-17-jre-headless wget && \
    apt-get clean

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# JCommander JAR dosyası
COPY jcommander.jar /app/jcommander.jar

# ZXing JAR dosyası
COPY javase-3.5.2.jar /app/javase-3.5.2.jar
COPY core-3.5.2.jar /app/core-3.5.2.jar

# Uygulama dosyaları
COPY . .

# Port (opsiyonel)
EXPOSE 5000

CMD ["python", "bot.py"]
