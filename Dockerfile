FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    git curl build-essential mariadb-client redis wget \
    nodejs npm yarn supervisor \
    && apt-get clean

# 安裝 frappe bench CLI
RUN pip install frappe-bench

# 建立 frappe 使用者與 bench 資料夾
RUN useradd -ms /bin/bash frappe
USER frappe
WORKDIR /home/frappe

# 初始化 bench 環境
RUN bench init --frappe-branch version-14 frappe-bench
WORKDIR /home/frappe/frappe-bench

# 複製啟動腳本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
