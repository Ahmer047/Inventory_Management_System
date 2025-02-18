FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create staticfiles directory and collect static files
RUN mkdir -p staticfiles

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "inventory_management_system.wsgi:application", "--bind", "0.0.0.0:8000"]