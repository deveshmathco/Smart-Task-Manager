# Smart Task Manager

A full-stack task management application with a FastAPI backend and a modern HTML/CSS/JavaScript frontend.

## Project Structure

- `app/` - Backend API server built with FastAPI
- `tag_server/` - Tag service API for generating task tags
- `client/` - Python command-line client for interacting with the API
- `frontend/` - Web frontend for the application

## Features

- Create, read, update, and delete tasks
- Batch create multiple tasks at once
- Mark tasks as complete or incomplete
- Filter tasks by status and priority
- Automatically tag tasks based on due date and priority
- Bulk operations for multiple tasks

## Backend Setup

### Prerequisites

- Python 3.7+
- FastAPI
- Uvicorn
- Requests

### Installation

1. Install the required packages:

```bash
pip install fastapi uvicorn requests
```

2. Start the tag server (required for the main API):

```bash
cd tag_server
uvicorn main:app --reload --port 8001
or
python -m uvicorn main:app --reload --port 8001
```

3. Start the main API server:

```bash
uvicorn main:app --reload --port 8000
or
python -m uvicorn main:app --reload --port 8000
```

## Frontend Setup

The frontend is a simple HTML/CSS/JavaScript application that can be served using any static file server.

### Running the Frontend

1. Ensure both the main API server and tag server are running
2. Navigate to the frontend directory:

```bash
cd frontend
```

3. Serve the files using a simple HTTP server:

```bash
# Using Python 3
python -m http.server 8080

# Using Python 2
python -m SimpleHTTPServer 8080
```

4. Open your browser and navigate to `http://localhost:8080`

## Command-Line Client

The project also includes a command-line client for interacting with the API.

### Usage

```bash
cd client
python client.py --help
```

Example commands:

```bash
# Create a new task
python client.py create --title "Example Task" --description "This is an example task" --due-date "2023-12-31" --priority "Medium"

# List all tasks
python client.py list

# List only completed tasks
python client.py list --completed true

# Mark a task as complete
python client.py complete 1

# Delete a task
python client.py delete 1
```

## API Documentation

When the main API server is running, visit `http://localhost:8000/docs` to access the Swagger UI documentation, which provides detailed information about all available endpoints.

## License

This project is open source and available under the [MIT License](LICENSE).
