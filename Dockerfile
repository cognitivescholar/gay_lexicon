# Use a slim Python 3.9 base image
FROM --platform=linux/amd64 python:3.9-slim-buster

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN apt-get update && apt-get install -y --no-install-recommends gcc
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --only-binary :all: "blis<1.3.0"
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --force-reinstall --no-cache-dir streamlit

# 🔥 Ensure punkt and punkt_tab are installed at build time
# 🔥 Download ALL required NLTK packages
RUN python -m nltk.downloader -d /usr/local/share/nltk_data \
    punkt \
    punkt_tab \
    stopwords \
    wordnet \
    averaged_perceptron_tagger \
    omw-1.4

# Copy the project files
COPY . /app/

EXPOSE 8501

CMD ["streamlit", "run", "main.py"]