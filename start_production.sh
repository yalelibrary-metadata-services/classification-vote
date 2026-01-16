#!/bin/bash
#
# Start the Classification Vote application with Gunicorn (production WSGI server)
#
# Usage:
#   ./start_production.sh [port]
#
# Default port is 5000 if not specified

PORT=${1:-5000}

echo "Starting Classification Vote application..."
echo "Server will be available at: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start gunicorn with:
# - 4 worker processes for handling concurrent requests
# - Bind to localhost on specified port
# - Access logs to stdout
# - Error logs to stderr
# - Worker timeout of 120 seconds for long-running requests
# - Graceful restart on code changes (in development)

gunicorn \
    --workers 4 \
    --bind "127.0.0.1:$PORT" \
    --access-logfile - \
    --error-logfile - \
    --timeout 120 \
    --reload \
    wsgi:app
