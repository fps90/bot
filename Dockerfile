FROM python:3.9
WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# تحديد الأمر لتشغيل البوت
CMD ["python", "bot.py"]
