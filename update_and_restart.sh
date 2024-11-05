#!/bin/sh

# Eventually this script will be changed/removed in favor of running the
# newest release. But for now it's the easiest option

cd /home/app/tigercart

# Pull the latest changes from the Git repository
/usr/local/bin/git fetch origin
LOCAL=$(/usr/local/bin/git rev-parse @)
REMOTE=$(/usr/local/bin/git rev-parse @{u})

# Check if there are updates in the remote repository
if [ "$LOCAL" != "$REMOTE" ]; then
    echo "New changes detected. Pulling changes..."
    /usr/local/bin/git pull origin main  # Replace 'main' with your branch name if different

    # Restart the server after pulling changes
    echo "Restarting Gunicorn for app and server..."
    doas /usr/bin/pkill -f "gunicorn --bind 127.0.0.1:8000"
    doas /usr/bin/pkill -f "gunicorn --bind 127.0.0.1:5150"
    sleep 10
    . tigercart_env/bin/activate

    # Restart server.py on port 5150
    gunicorn --bind 127.0.0.1:5150 server:app --workers 5 &

    # Restart app.py on port 8000
    gunicorn --bind 127.0.0.1:8000 app:app --workers 5 &
else
    echo "No changes detected. No restart needed."
fi
