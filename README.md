# Shut the Box

A Progressive Web App (PWA) implementation of the classic dice game "Shut the Box" built with Python and Flask.

## About the Game

Shut the Box is a classic dice game where players roll a pair of dice and flip down corresponding numbered tiles on a board. The goal is to "shut the box" by closing all tiles, or to have the lowest score by summing the remaining numbers when no more moves can be made.

### Game Rules

1. Players roll a pair of dice each round
2. All players play with the same rolled number per round
3. Each player must flip down one or more tiles that sum to the dice total
4. If a player cannot make a valid move, they are out and their score is the sum of remaining tiles
5. The game ends when one player shuts the box (closes all tiles) or no players can make a move
6. The player with the lowest score wins

### Features

- Support for 1-12 players per game
- Configurable tile count (1-10 or 1-12)
- Real-time multiplayer gameplay
- PWA support for mobile installation on Android and iOS
- Simple username/password authentication

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Quick Setup (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/thiagoralves/shut-the-box.git
   cd shut-the-box
   ```

2. Run the installation script:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. Run the application:
   ```bash
   ./run_app.sh
   ```

4. Open your browser and navigate to `http://localhost:8000`

### Manual Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/thiagoralves/shut-the-box.git
   cd shut-the-box
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and set your SECRET_KEY
   ```

5. Run the application:
   ```bash
   python run.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
shut-the-box/
├── app/
│   ├── __init__.py      # Flask app factory
│   ├── auth.py          # Authentication routes
│   ├── models.py        # Database models
│   └── routes.py        # Main routes
├── static/
│   ├── css/
│   │   └── style.css    # Application styles
│   ├── icons/           # PWA icons
│   ├── js/
│   │   └── sw.js        # Service worker
│   └── manifest.json    # PWA manifest
├── templates/
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── login.html       # Login page
│   └── signup.html      # Sign up page
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
├── run.py              # Development entry point
├── wsgi.py             # Production WSGI entry point
├── install.sh          # Installation script
├── run_app.sh          # Production startup script
└── README.md           # This file
```

## PWA Installation

### Android
1. Open the app in Chrome
2. Tap the menu (three dots) and select "Add to Home screen"
3. Follow the prompts to install

### iOS
1. Open the app in Safari
2. Tap the Share button
3. Select "Add to Home Screen"
4. Tap "Add" to confirm

## Development

### Running in Development Mode

```bash
python run.py
```

The app will run with debug mode enabled and auto-reload on code changes.

### Production Deployment

For production, use the provided `run_app.sh` script which uses gunicorn:

```bash
./run_app.sh
```

Or use gunicorn directly:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

Make sure to:
- Set a strong `SECRET_KEY` in your environment
- Use a production database (PostgreSQL recommended)
- Configure HTTPS

### Running as a Systemd Service

To run the application as a background service that starts automatically on boot:

1. Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/shut-the-box.service
   ```

2. Add the following content (adjust paths as needed):
   ```ini
   [Unit]
   Description=Shut the Box Game
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/shut-the-box
   ExecStart=/home/ubuntu/shut-the-box/venv/bin/gunicorn -w 4 -b 127.0.0.1:8001 wsgi:app
   Restart=always
   RestartSec=3
   EnvironmentFile=/home/ubuntu/shut-the-box/.env

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable shut-the-box
   sudo systemctl start shut-the-box
   ```

4. Check the service status:
   ```bash
   sudo systemctl status shut-the-box
   ```

### Nginx Configuration for Custom Domain

To serve the application behind nginx with a custom domain (e.g., `shutthebox.yourdomain.com`):

1. Create an nginx configuration file:
   ```bash
   sudo nano /etc/nginx/sites-available/shut-the-box
   ```

2. Add the following configuration:
   ```nginx
   server {
       listen 80;
       server_name shutthebox.yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8001;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_cache_bypass $http_upgrade;
       }

       # PWA manifest - served directly from static folder
       location = /manifest.json {
           alias /home/ubuntu/shut-the-box/static/manifest.json;
           default_type application/manifest+json;
       }

       # PWA service worker - served directly from static folder
       # Important: Don't cache aggressively to allow updates
       location = /sw.js {
           alias /home/ubuntu/shut-the-box/static/js/sw.js;
           default_type application/javascript;
           add_header Cache-Control "no-cache";
           add_header Service-Worker-Allowed /;
       }

       location /static {
           alias /home/ubuntu/shut-the-box/static;
           expires 30d;
           add_header Cache-Control "public, immutable";
       }
   }
   ```
   
   **Important for PWA:** The `location = /manifest.json` and `location = /sw.js` blocks are required for the Progressive Web App to install correctly on mobile devices. These serve the PWA files directly from nginx (more efficient than proxying to Flask).

3. Enable the site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/shut-the-box /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

4. Set up SSL with Let's Encrypt (recommended):
   ```bash
   sudo certbot --nginx -d shutthebox.yourdomain.com
   ```

### DNS Configuration for Custom Domain

To use a custom domain for the shut-the-box game:

1. Go to your DNS provider (e.g., Route 53, Cloudflare, GoDaddy)

2. Create an A record pointing to your server's IP address:
   - Type: A
   - Name: shutthebox (or your preferred subdomain)
   - Value: Your server's public IP address
   - TTL: 300 (or your preferred TTL)

3. Wait for DNS propagation (can take up to 48 hours, but usually much faster)

4. Once DNS is propagated, access your app at `http://shutthebox.yourdomain.com`

### Running Multiple Apps on the Same Server

If you're running multiple Flask apps (e.g., options-dashboard and shut-the-box) on the same server:

1. Each app should run on a different port (e.g., options-dashboard on 8000, shut-the-box on 8001)

2. Create separate nginx configuration files for each app with different `server_name` values

3. Each app can have its own domain or subdomain:
   - `dashboard.yourdomain.com` -> proxy to port 8000
   - `shutthebox.yourdomain.com` -> proxy to port 8001

4. Use separate systemd service files for each application

## License

This project is for personal use among family and friends.

## Contributing

This is a personal project, but suggestions and feedback are welcome!
