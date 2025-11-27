# Stage 1: Builder
# Use a slim Python image as the base for building dependencies
FROM python:3.12-slim AS builder

# Set the working directory inside the container
WORKDIR /app

# Install build dependencies for swisseph and pyswisseph
# These might include gcc, python3-dev, etc.
# For slim-buster, these are usually sufficient.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .
# Install Python dependencies into a wheelhouse for efficient caching
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Stage 2: Runtime
# Use a slim Python image as the base for the final application
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the necessary runtime dependencies from the builder stage
COPY --from=builder /wheels /wheels
# Install the pre-built Python dependencies from the wheelhouse
RUN pip install --no-cache-dir /wheels/*

# Copy all application files into the container
COPY . /app

# Expose the port the API runs on
EXPOSE 9021

# Command to run the API using uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "9021"]