Here's a detailed INSTALLATION.md file for Windows users:

````markdown
# ATL Tours Application - Windows Installation Guide

## Prerequisites

1. **Docker Desktop for Windows**

   - Download from [Docker's official website](https://www.docker.com/products/docker-desktop)
   - Install Docker Desktop
   - During installation, accept WSL 2 installation if prompted
   - Restart your computer after installation

2. **Git** (if not already installed)
   - Download from [Git's official website](https://git-scm.com/download/windows)
   - Use default installation settings

## Installation Steps

### 1. Clone the Repository

```bash
# Open Command Prompt or PowerShell and run:
git clone <repository-url>
cd atl
```
````

### 2. Environment Setup

1. Create a file named `.env` in the project root directory
2. Add the following environment variables:

```env
MYSQL_ROOT_PASSWORD=your_password
MYSQL_DATABASE=atl
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
```

### 3. Docker Setup

1. Open Docker Desktop
2. Wait for Docker engine to start (check status in bottom-left corner)
3. Open Command Prompt or PowerShell in project directory

### 4. Build and Run

```bash
# Build and start containers
docker-compose -f docker-compose.dev.yml up --build

# To stop the application
# Press Ctrl+C in the terminal
```

### 5. Verify Installation

1. Open your web browser
2. Visit: `http://localhost:5001`
3. You should see the ATL Tours homepage

## Database Access

- Host: localhost
- Port: 3306
- Database: atl
- Username: (from .env file)
- Password: (from .env file)

## Common Issues and Solutions

### Port Conflicts

If you see errors about ports being in use:

1. Check if MySQL (port 3306) is running locally
2. Check if port 5001 is in use

```bash
# Check ports in use (PowerShell)
netstat -ano | findstr "3306"
netstat -ano | findstr "5001"
```

### Docker Issues

If Docker isn't starting:

1. Verify Docker Desktop is running
2. Check Windows Features:
   - Open Windows Features
   - Ensure "Windows Subsystem for Linux" is enabled
   - Ensure "Virtual Machine Platform" is enabled

### Volume Mounting Issues

If you see volume mounting errors:

1. Open Docker Desktop
2. Go to Settings > Resources > File Sharing
3. Add your project directory to shared folders

## Useful Commands

```bash
# View running containers
docker ps

# Stop all containers
docker-compose -f docker-compose.dev.yml down

# View logs
docker-compose -f docker-compose.dev.yml logs

# Rebuild specific service
docker-compose -f docker-compose.dev.yml up --build <service-name>

# Remove all containers and volumes
docker-compose -f docker-compose.dev.yml down -v
```

## Project Structure

```
atl/
├── app/
│   ├── routes/
│   ├── templates/
│   └── static/
├── db/
├── docker-compose.dev.yml
├── Dockerfile
└── requirements.txt
```

## Troubleshooting

### Database Connection Issues

If MySQL container isn't connecting:

1. Wait 30 seconds after container startup
2. Check logs: `docker-compose -f docker-compose.dev.yml logs db`
3. Verify environment variables in .env file

### Web Application Issues

If Flask app isn't starting:

1. Check logs: `docker-compose -f docker-compose.dev.yml logs web`
2. Verify Python dependencies in requirements.txt
3. Check for port conflicts

### File Permission Issues

If you see permission errors:

1. Run PowerShell as Administrator
2. Check file permissions in project directory
3. Verify Docker Desktop has necessary permissions

## Support

If you encounter any issues:

1. Check Docker Desktop logs
2. Verify all prerequisites are installed
3. Contact project maintainers with:
   - Error messages
   - Docker logs
   - Windows version
   - Docker Desktop version

## Development Workflow

1. Make changes to code
2. Docker will automatically reload Flask application
3. If adding new dependencies:
   - Add to requirements.txt
   - Rebuild containers: `docker-compose -f docker-compose.dev.yml up --build`

## Security Notes

- Never commit .env file
- Keep Docker Desktop updated
- Use strong passwords in .env file
- Follow security best practices for production deployment

```

Would you like me to add any additional sections or provide more detailed information about specific aspects?
```
