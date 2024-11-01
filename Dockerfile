FROM python:3.9-slim

WORKDIR /bot

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8050

CMD ["python", "app.py"]
