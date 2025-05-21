FROM bitnami/spark:latest

COPY etl_job.py /app/etl_job.py
COPY data /mnt/data/
COPY jars/postgresql-42.6.2.jar /opt/bitnami/spark/jars/

WORKDIR /app

# ✅ Corrige l’erreur "basedir must be absolute"
ENV HOME=/tmp

CMD ["spark-submit", "/app/etl_job.py"]