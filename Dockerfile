# Base Python image for running the AI Employee Query Chatbo
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies, add SQL Server ODBC connectivity (pyodbc) & command line tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    gcc \
    g++ \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 mssql-tools18 \
    && echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc \
    && rm -rf /var/lib/apt/lists/*
    # remove metadata which is gathered when installing dependency

# Copy dependency file separately to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir  -r requirements.txt

# Copy application source code
COPY . .

# Start the application
CMD ["python", "main.py"]