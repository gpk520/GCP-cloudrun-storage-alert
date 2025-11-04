FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV FUNCTION_TARGET=set_object_access_policy
CMD ["functions-framework", "--target", "set_object_access_policy", "--port", "8080"]
