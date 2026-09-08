# Fixture environment for the HANDOFF example tasks (F2, F5, F10).
#
# Deliberately minimal and offline: the tasks are investigations over a small
# Python service, and a narrow image is how the tool surface gets enforced
# (DESIGN.md 8.1 -- you cannot call a binary that is not installed).
FROM python:3.11-slim

RUN pip install --no-cache-dir pytest==8.3.3

WORKDIR /workspace
COPY repo/ /workspace/

# No git history: these tasks are about reading code, and a log would leak the
# planted defects. Absence of git also makes the git_push hard-fail unreachable
# by accident rather than by discipline, so scope discipline is measured on
# filesystem effects here.
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["/bin/bash"]
