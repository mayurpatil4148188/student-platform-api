#!/bin/bash

# Student Platform API - Production Deployment Script
# This script handles the complete deployment process for production

set -e  # Exit on any error

# Configuration
APP_NAME="student-platform-api"
APP_DIR="/opt/student-platform-api"
VENV_DIR="/opt/student-platform-api/venv"
SERVICE_USER="student-api"
LOG_DIR="/var/log/student-platform-api"
NGINX_CONF="/etc/nginx/sites-available/student-platform-api"
SYSTEMD_SERVICE="/etc/systemd/system/student-platform-api.service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
    fi
}

# Install system dependencies
install_system_dependencies() {
    log "Installing system dependencies..."
    
    # Update package list
    apt-get update
    
    # Install required packages
    apt-get install -y \
        python3.12 \
        python3.12-venv \
        python3.12-dev \
        postgresql \
        postgresql-contrib \
        nginx \
        redis-server \
        git \
        curl \
        build-essential \
        libpq-dev \
        supervisor
    
    log "System dependencies installed successfully"
}

# Create application user
create_app_user() {
    log "Creating application user..."
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/false -d "$APP_DIR" "$SERVICE_USER"
        log "User $SERVICE_USER created"
    else
        log "User $SERVICE_USER already exists"
    fi
}

# Setup application directory
setup_app_directory() {
    log "Setting up application directory..."
    
    # Create directories
    mkdir -p "$APP_DIR"
    mkdir -p "$LOG_DIR"
    
    # Set permissions
    chown -R "$SERVICE_USER:$SERVICE_USER" "$APP_DIR"
    chown -R "$SERVICE_USER:$SERVICE_USER" "$LOG_DIR"
    
    log "Application directory setup complete"
}

# Setup PostgreSQL database
setup_database() {
    log "Setting up PostgreSQL database..."
    
    # Start PostgreSQL service
    systemctl start postgresql
    systemctl enable postgresql
    
    # Create database and user
    sudo -u postgres psql << EOF
CREATE DATABASE student_platform_prod;
CREATE USER student_api_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE student_platform_prod TO student_api_user;
\q
EOF
    
    log "Database setup complete"
}

# Deploy application code
deploy_application() {
    log "Deploying application code..."
    
    # Clone or update repository
    if [ -d "$APP_DIR/.git" ]; then
        cd "$APP_DIR"
        sudo -u "$SERVICE_USER" git pull origin main
    else
        # Replace with actual repository URL
        git clone https://github.com/your-org/student-platform-api.git "$APP_DIR"
        chown -R "$SERVICE_USER:$SERVICE_USER" "$APP_DIR"
    fi
    
    # Create virtual environment
    if [ ! -d "$VENV_DIR" ]; then
        sudo -u "$SERVICE_USER" python3.12 -m venv "$VENV_DIR"
    fi
    
    # Activate virtual environment and install dependencies
    sudo -u "$SERVICE_USER" bash -c "
        source $VENV_DIR/bin/activate
        pip install --upgrade pip
        pip install -r $APP_DIR/requirements.txt
    "
    
    log "Application code deployed successfully"
}

# Setup environment configuration
setup_environment() {
    log "Setting up environment configuration..."
    
    # Create production environment file
    sudo -u "$SERVICE_USER" cat > "$APP_DIR/.env" << EOF
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=postgresql://student_api_user:secure_password_here@localhost:5432/student_platform_prod
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
LOG_FILE=$LOG_DIR/app.log
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
EOF
    
    log "Environment configuration created"
}

# Initialize database
initialize_database() {
    log "Initializing database..."
    
    sudo -u "$SERVICE_USER" bash -c "
        cd $APP_DIR
        source $VENV_DIR/bin/activate
        export FLASK_APP=run.py
        flask db init
        flask db migrate -m 'Initial migration'
        flask db upgrade
    "
    
    log "Database initialized successfully"
}

# Setup systemd service
setup_systemd_service() {
    log "Setting up systemd service..."
    
    cat > "$SYSTEMD_SERVICE" << EOF
[Unit]
Description=Student Platform API
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$VENV_DIR/bin
ExecStart=$VENV_DIR/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 --timeout 120 --access-logfile $LOG_DIR/access.log --error-logfile $LOG_DIR/error.log run:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable student-platform-api
    systemctl start student-platform-api
    
    log "Systemd service setup complete"
}

# Setup Nginx reverse proxy
setup_nginx() {
    log "Setting up Nginx reverse proxy..."
    
    cat > "$NGINX_CONF" << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration (replace with your certificates)
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    # Proxy configuration
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Static files (if any)
    location /static/ {
        alias $APP_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
}
EOF
    
    # Enable site
    ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
    nginx -t
    systemctl reload nginx
    
    log "Nginx configuration complete"
}

# Setup monitoring and logging
setup_monitoring() {
    log "Setting up monitoring and logging..."
    
    # Setup log rotation
    cat > /etc/logrotate.d/student-platform-api << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $SERVICE_USER $SERVICE_USER
    postrotate
        systemctl reload student-platform-api
    endscript
}
EOF
    
    # Setup basic monitoring script
    cat > /usr/local/bin/check-student-api.sh << 'EOF'
#!/bin/bash
# Basic health check script

API_URL="http://localhost:5000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL")

if [ "$RESPONSE" = "200" ]; then
    echo "API is healthy"
    exit 0
else
    echo "API is unhealthy (HTTP $RESPONSE)"
    exit 1
fi
EOF
    
    chmod +x /usr/local/bin/check-student-api.sh
    
    # Add to crontab for regular health checks
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/check-student-api.sh") | crontab -
    
    log "Monitoring setup complete"
}

# Main deployment function
main() {
    log "Starting Student Platform API deployment..."
    
    check_root
    install_system_dependencies
    create_app_user
    setup_app_directory
    setup_database
    deploy_application
    setup_environment
    initialize_database
    setup_systemd_service
    setup_nginx
    setup_monitoring
    
    log "Deployment completed successfully!"
    log "API is available at: https://yourdomain.com"
    log "API Documentation: https://yourdomain.com/docs/"
    log "Health Check: https://yourdomain.com/health"
    
    warning "Please update the following before going live:"
    warning "1. Replace 'yourdomain.com' with your actual domain"
    warning "2. Update SSL certificates in Nginx configuration"
    warning "3. Change database password in .env file"
    warning "4. Update CORS_ORIGINS with your frontend domains"
    warning "5. Configure firewall rules"
}

# Run main function
main "$@"
