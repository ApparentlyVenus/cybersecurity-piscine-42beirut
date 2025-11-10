FROM python:3.11-slim

RUN pip install --no-cache-dir cryptography

RUN mkdir -p /root/infection
RUN mkdir -p /app

COPY src/Stockholm /app/Stockholm
COPY src/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/Stockholm
RUN chmod +x /app/entrypoint.sh

WORKDIR /root

CMD ["/bin/bash", "-c", "/app/entrypoint.sh && exec /bin/bash"]