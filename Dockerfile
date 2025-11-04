# Stage 1: Build the necessary dependencies
# Use a Python base image with the required version
FROM python:3.11-slim as builder

# Set the working directory for the build process
WORKDIR /app

# Copy the requirements file and install dependencies
# We use --no-cache-dir to keep the layer small
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---

# Stage 2: Final image - Use a clean, smaller base image for production
FROM python:3.11-slim

# Set the working directory for the final application
WORKDIR /app

# Copy only the installed packages from the builder stage
# This ensures a much smaller final image than copying the entire build stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the application source code
COPY main.py .

# Expose the port that the service will listen on (default for Cloud Run is 8080)
# This is mainly for documentation/tools but is often omitted as Cloud Run handles it
EXPOSE 8080

# Set the environment variable for the entry point
# Cloud Run functions rely on the FUNCTIONS_FRAMEWORK to know the entry point
ENV FUNCTION_TARGET=set_object_access_policy

# Run the functions-framework web server
# The port is pulled from the environment variable PORT provided by Cloud Run
CMD ["functions-framework", "--target", "set_object_access_policy", "--port", "8080"]
