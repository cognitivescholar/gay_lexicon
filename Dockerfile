# Use a slim Python 3.9 base image
FROM --platform=linux/amd64 python:3.9-slim-buster

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --only-binary :all: "blis<1.3.0"
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --force-reinstall --no-cache-dir streamlit

# 🔥 Ensure nltk downloads persist 🔥
RUN python -m nltk.downloader punkt stopwords

# Copy the project files
COPY . /app/

EXPOSE 8501

CMD ["streamlit", "run", "main.py"]