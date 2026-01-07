FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY launcher.py .
COPY src/ src/
COPY web/ web/
COPY conf/logging.json conf/
RUN mkdir -p conf/runners

EXPOSE 5000
CMD [ "python3", "launcher.py" ]
