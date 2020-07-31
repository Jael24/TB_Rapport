ARG elastic_stack
FROM docker.elastic.co/beats/metricbeat:${elastic_stack}
COPY config/metricbeat.yml /usr/share/metricbeat/metricbeat.yml
USER root
RUN chown root:metricbeat /usr/share/metricbeat/metricbeat.yml
