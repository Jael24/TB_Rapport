ARG elastic_version
FROM docker.elastic.co/beats/filebeat:${elastic_version}
COPY config/filebeat.yml /usr/share/filebeat/filebeat.yml
USER root
RUN chown root:filebeat /usr/share/filebeat/filebeat.yml
USER filebeat
