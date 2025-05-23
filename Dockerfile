FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir: Disables the pip cache, leading to smaller image sizes.
# -r requirements.txt: Specifies the file from which to read package requirements.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application script into the container at /app
COPY app.py .

# Specify the command to run on container start
CMD ["python", "app.py"]
