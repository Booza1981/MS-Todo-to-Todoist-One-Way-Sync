FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy
WORKDIR /app
COPY src/ /app/src/
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "-m", "src.main"]