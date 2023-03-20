FROM python:3.11.1

# Copy project files
RUN mkdir /app
WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

EXPOSE 7270 8080

# Run the app
CMD ["python", "webserver_api.py"]