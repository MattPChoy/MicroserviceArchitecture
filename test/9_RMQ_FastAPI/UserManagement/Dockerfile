# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
RUN mkdir /app
WORKDIR /app

# Copy the requirements file into the container
COPY UserManagement/requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY UserManagement/ /app/

# Expose port 8001 for FastAPI
EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "user_management:app", "--host", "0.0.0.0", "--port", "8001"]
