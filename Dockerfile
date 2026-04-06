FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV OPENAI_API_KEY=""

EXPOSE 8000

CMD ["python", "api.py"]
