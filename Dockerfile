# Use an optimized Python image
FROM --platform=linux/amd64 python:3.9-slim-buster

# Set working directory
WORKDIR /app

# Copy the requirements file first
COPY requirements.txt /app/

# Install required system dependencies (libpq-dev fixes psycopg2 issues)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download required NLP data
RUN python -m nltk.downloader -d /usr/local/share/nltk_data \
    punkt stopwords wordnet averaged_perceptron_tagger punkt_tab

# Install SpaCy model explicitly
RUN python -m spacy download en_core_web_sm

# Copy the entire project files into the container
COPY . /app/

# Expose the port (if needed)
EXPOSE 8080

# Set the default command
CMD ["python", "main.py"]
