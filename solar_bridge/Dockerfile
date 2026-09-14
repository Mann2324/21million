FROM python:3.12-slim
WORKDIR /app
COPY server.py /app/server.py
COPY requirements.txt /app/requirements.txt
EXPOSE 10000
CMD ["python", "-u", "server.py"]
