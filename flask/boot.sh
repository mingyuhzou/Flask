#!/bin/sh
. venv/bin/activate
while true; do
    flask deploy
    if [ "$?" -eq 0 ]; then
        break
    fi
    echo "Deploy command failed. Retrying in 5 sec..."
    sleep 5
done

# 启动 gunicorn
exec gunicorn -b 0.0.0.0:5000 --access-logfile - --error-logfile - run:app
