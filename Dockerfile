FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py aws_billing.py dashboard.html ./

EXPOSE 8000

CMD ["python", "main.py"]