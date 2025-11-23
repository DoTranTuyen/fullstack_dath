# Use Python 3.11 base image
FROM python:3.11
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . .

# Upgrade pip and install dependencies
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m pip install uwsgi daphne

# Define the build argument
ARG SERVICE=web  # Default service is web
ENV SERVICE=${SERVICE}

# Command to start either uwsgi or daphne depending on the service
CMD ["sh", "-c", "if [ \"$SERVICE\" = \"web\" ]; then uwsgi --http=0.0.0.0:80 --module=core.wsgi; else daphne -b 0.0.0.0 -p 5000 core.asgi:application; fi"]
