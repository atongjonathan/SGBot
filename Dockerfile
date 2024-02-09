# Use the official Python image as a base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the entire project into the container
COPY . /app/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the bot will run on
EXPOSE 80

# Run the bot script when the container is started
CMD ["python", "main.py"]
