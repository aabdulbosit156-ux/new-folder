# Yengil va tezkor Python 3.11 versiyasidan foydalanamiz
FROM python:3.11-slim

# Python loglari terminalda darhol ko'rinishi uchun
ENV PYTHONUNBUFFERED=1

# Konteyner ichida ishchi papkani belgilaymiz
WORKDIR /app

# Eng muhimi: pydub audio formatlarini o'zgartirishi uchun FFmpeg o'rnatamiz
# Va keraksiz kesh larni tozalaymiz (konteyner hajmi kichik bo'lishi uchun)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Barcha kerakli Python kutubxonalarini o'rnatamiz
RUN pip install --no-cache-dir aiogram SpeechRecognition pydub

# Loyihadagi bot.py faylini konteynerga nusxalaymiz
COPY bot.py .

# Konteyner ishga tushganda botni yurgizish buyrug'i
CMD ["python", "bot.py"]