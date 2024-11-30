FROM apache/airflow:latest

# Switch to the root user to perform system-level operations
USER root

# Install system-level dependencies
RUN apt-get update && \
    apt-get -y install git && \
    apt-get clean

# Switch back to the airflow user
USER airflow

# Set the working directory to the airflow user home directory
WORKDIR /opt/airflow

# Copy the requirements.txt file into the image
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
