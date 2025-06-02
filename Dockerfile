FROM bitnami/spark:latest

# Install OpenJDK 11 (required for PySpark)
USER root
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME and update PATH
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Copy your files
COPY etl_job.py /app/etl_job.py
COPY data /data/
COPY jars/postgresql-42.6.2.jar /opt/bitnami/spark/jars/

# Set working directory
WORKDIR /app

# Final command (runs PySpark ETL job)
CMD ["spark-submit", "/app/etl_job.py"]