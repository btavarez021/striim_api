# Build stage
FROM python:3.10-slim AS build-stage
# Set the working directory in the container
WORKDIR /striim_app_api
# Copy requirements.txt into the working directory
COPY requirements.txt .
# Install build-time dependencies and Python packages
RUN apt-get update && \
   apt-get install -y --no-install-recommends \
   gcc \
   g++ \
   unixodbc-dev \
   curl \
&& pip install --no-cache-dir -r requirements.txt \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
# Runtime stage (final image)
FROM python:3.10-slim AS runtime-stage
# Set the working directory in the container
WORKDIR /striim_app_api
# Copy installed Python packages from build stage to runtime stage
COPY --from=build-stage /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=build-stage /usr/local/bin /usr/local/bin
# Install runtime dependencies (only what’s needed to run the app)
RUN apt-get update && \
   apt-get install -y --no-install-recommends \
   unixodbc \
   curl \
   ca-certificates \
   gnupg2 \
   dpkg \
   lsb-release \
   libterm-readline-gnu-perl \
   odbcinst\
&& curl -k https://packages.microsoft.com/ubuntu/20.04/prod/pool/main/m/msodbcsql17/msodbcsql17_17.10.1.1-1_amd64.deb -o msodbcsql17.deb \
&& ACCEPT_EULA=Y dpkg -i msodbcsql17.deb \
&& apt-get install -f -y \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* msodbcsql17.deb
# Copy app files
COPY . .
# Expose port 5000 for the Flask app
EXPOSE 5000
# Set environment variables for Flask
ENV FLASK_APP=ship_app.py
ENV FLASK_DEBUG=development
# Ensure proper logging for container environments
ENV PYTHONUNBUFFERED=1
# Command to run the Flask app using hypercorn with live reload
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "ship_app:app", "--bind", "0.0.0.0:5000"]