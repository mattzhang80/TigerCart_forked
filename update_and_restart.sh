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
    echo "Restarting Gunicorn..."
    doas /usr/bin/pkill -f "gunicorn --bind 127.0.0.1:8000"
    sleep 5
    . tigercart_env/bin/activate
    gunicorn --bind 127.0.0.1:8000 app:app --workers 5 &
else
    echo "No changes detected. No restart needed."
fi
