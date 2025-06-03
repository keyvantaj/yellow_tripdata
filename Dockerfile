FROM bitnami/spark:latest

COPY etl_job.py /app/etl_job.py
COPY data /data/
COPY jars/postgresql-42.6.2.jar /opt/bitnami/spark/jars/

RUN apt-get update && apt-get install -y openjdk-11-jdk && \
    ln -s /usr/lib/jvm/java-11-openjdk-amd64 /opt/bitnami/java

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

ENV PATH=$JAVA_HOME/bin:$PATH
ENV HOME=/tmp

WORKDIR /app

CMD ["spark-submit", "/app/etl_job.py"]