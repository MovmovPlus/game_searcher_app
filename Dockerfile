# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/app/requirements.txt

# Define the Flask application environment variable
ENV FLASK_APP app/main.py

# Expose the port on which your app will run
EXPOSE 5000

# Define the command to run your app using Flask's built-in server
CMD ["flask", "run", "--host=0.0.0.0"]
