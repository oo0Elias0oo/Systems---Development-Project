# Dev / simple build
FROM python:3.13-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port used by Flask dev server
EXPOSE 5000

# Default command (dev)
CMD ["python", "app.py"]
