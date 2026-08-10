FROM python:3.11-alpine

# Install android-tools (adb) and shadow
RUN apk add --no-cache android-tools bash

WORKDIR /app

# Copy package files
COPY pyproject.toml setup.py README.md LICENSE ./
COPY tv_control_center ./tv_control_center

# Install package
RUN pip install --no-cache-dir -e .

EXPOSE 8888

ENV ADB_TARGET="192.168.2.122:5555"

CMD ["bravia-control", "serve", "--port", "8888"]
