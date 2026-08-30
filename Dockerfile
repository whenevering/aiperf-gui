FROM nvcr.io/nvidia/ai-dynamo/aiperf:0.12.0

WORKDIR /opt/aiperf-gui

COPY app/ /opt/aiperf-gui/app/

ENV AIPERF_DATA_DIR=/data/results
EXPOSE 8080

USER 0
ENTRYPOINT []
CMD ["python3", "/opt/aiperf-gui/app/app.py"]
