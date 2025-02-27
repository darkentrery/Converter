#!/bin/sh
while true; do
  # Ждем файлов для обработки или выполняем другую работу
  echo "Processing..."
  sleep 3600
done
exec "$@"
