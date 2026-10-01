FROM registry.fedoraproject.org/fedora:latest

# Install Python 3, Jinja2, and PyYAML
RUN dnf install -y python3 python3-jinja2 python3-pyyaml && \
    dnf clean all

WORKDIR /app

COPY process_templates.py /app/process_templates.py
RUN chmod +x /app/process_templates.py

RUN mkdir -p /data /data/output

ENTRYPOINT ["python3", "/app/process_templates.py"]

