FROM bitnami/spark:latest

COPY etl_job.py /app/etl_job.py
COPY data /data/
COPY jars/postgresql-42.6.2.jar /opt/bitnami/spark/jars/
RUN apt-get update && apt-get install -y openjdk-11-jdk

WORKDIR /app
RUN install_packages openjdk-11-jdk

# ✅ Corrige l’erreur "basedir must be absolute"
ENV HOME=/tmp
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

CMD ["spark-submit", "/app/etl_job.py"]