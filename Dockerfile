# Stage 1: Build the Svelte frontend
FROM node:20-slim AS frontend-builder

# Set the working directory
WORKDIR /app/frontend

# Copy package configuration and install dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/ .

# Build the application
RUN npm run build

# --- 

# Stage 2: Build the Python backend
FROM python:3.11-slim AS backend-runner

# Set the working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy only the necessary files for dependency installation
COPY backend/requirements.txt .

# Install Python dependencies using uv
RUN uv pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY backend/ ./backend/

# Copy the main configuration file
COPY app.yaml .

# Copy the built frontend from the builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Define mount points for persistent data and plugins.
# These folders can be mapped to host directories using docker run -v
VOLUME /app/data
VOLUME /app/plugins

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# We use uvicorn directly for production.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
