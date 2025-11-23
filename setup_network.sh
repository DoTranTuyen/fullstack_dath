#!/bin/bash

DOMAINS=("app.rms" "app.manage.rms")
HOSTS_FILE="/etc/hosts"

# Lấy IP local (trừ loạt 127.x và Docker)
IP=$(ipconfig getifaddr en0 2>/dev/null || \
     ipconfig getifaddr en1 2>/dev/null || \
     ifconfig | grep 'inet ' | grep -v 127 | grep -v docker | awk '{print $2}' | head -n 1)

if [ -z "$IP" ]; then
    echo "[✘] Không lấy được IP nội bộ."
    exit 1
fi

echo "[i] IP nội bộ hiện tại: $IP"

for DOMAIN in "${DOMAINS[@]}"
do
    # Xóa dòng cũ nếu tồn tại
    if grep -q "$DOMAIN" "$HOSTS_FILE"; then
        echo "[~] Đã tồn tại domain $DOMAIN. Cập nhật IP..."
        sudo sed -i '' "/$DOMAIN/d" "$HOSTS_FILE"   # macOS
    fi

    # Thêm dòng mới
    echo "$IP    $DOMAIN" | sudo tee -a "$HOSTS_FILE" > /dev/null

    if [ $? -eq 0 ]; then
        echo "[✔] Đã cập nhật: http://$DOMAIN"
    else
        echo "[✘] Không thể cập nhật $DOMAIN. Hãy chạy script bằng quyền sudo."
    fi
done
