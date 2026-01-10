# Use Python 3.9
FROM python:3.9

# Set the working directory
WORKDIR /code

# Copy requirements and install them
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy all files
COPY . .

# Grant permissions (important for some cloud environments)
RUN chmod -R 777 /code

# Run the app
CMD ["python", "app.py"]