FROM python:3.12-slim
WORKDIR /workspace
COPY workspace/ /workspace/
COPY opt/ /opt/
RUN chmod +x /opt/svcctl/svcctl && ln -s /opt/svcctl/svcctl /usr/local/bin/svcctl
ENV SVCCTL_LATENCY=2
