# Smart Task Manager Frontend

A clean, modern UI for the Smart Task Manager application. This frontend integrates with the FastAPI backend to provide a complete task management solution.

## Features

- Create, view, edit, and delete tasks
- Batch create multiple tasks at once
- Mark tasks as complete or incomplete
- Filter tasks by status and priority
- Bulk operations on selected tasks
- Modern, responsive design

## Setup Instructions

1. Ensure the backend server is running on http://localhost:8000
2. Ensure the tag server is also running on http://localhost:8001
3. Open `index.html` in a modern web browser

## Running with a Web Server

For the best experience, serve the files using a simple web server. There are several ways to do this:

### Using Python

```bash
# Python 3
python -m http.server 8080

# Python 2
python -m SimpleHTTPServer 8080
```

Then visit `http://localhost:8080` in your browser.

### Using Node.js

Install a simple server like `http-server`:

```bash
npm install -g http-server
http-server -p 8080
```

Then visit `http://localhost:8080` in your browser.

## Browser Compatibility

The frontend is compatible with all modern browsers:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Technology Used

- HTML5
- CSS3 (with CSS Variables and Flexbox/Grid)
- Vanilla JavaScript (ES6+)
- Font Awesome for icons

## Code Organization

- `index.html` - Main HTML file
- `css/styles.css` - Styles for the application
- `js/api.js` - API service for communicating with the backend
- `js/ui.js` - UI helper functions
- `js/app.js` - Main application logic

## Features Overview

### Task Management
- View tasks in a clean, sortable list
- Create new tasks with title, description, due date, priority, and completion status
- Edit existing tasks
- Delete tasks with confirmation
- Batch create multiple tasks at once

### Filtering and Sorting
- Filter tasks by completion status (complete/incomplete)
- Filter tasks by priority level (Low/Medium/High)

### Bulk Operations
- Select multiple tasks using checkboxes
- Mark selected tasks as complete/incomplete
- Delete selected tasks

### Responsive Design
- Works on desktop, tablet, and mobile devices
- Adapts layout based on screen size 