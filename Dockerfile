FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Bu qatordagi collectstaticni olib tashlang:
# RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Gunicornni ishga tushirishdan oldin collectstaticni amalga oshiramiz
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000 & python manage.py bot & wait"]
