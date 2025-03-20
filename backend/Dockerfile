FROM python:3.13-slim

WORKDIR /wikipedia-knowledge-explorer

# Install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "wiki.main:wiki_exp", "--host", "0.0.0.0", "--port", "8000"]
