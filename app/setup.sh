#!/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
RED='\033[0;31m'Th
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RESET='\033[0m'

# Function to display menu
show_menu() {
    echo -e "${CYAN}Options:${RESET}"
    echo "1. Build all images and start services"
    echo "2. Build and start the web service"
    echo "3. Build and start the database service"
    echo "4. Build and start the socket service"
    echo "5. Run Django migrations"
    echo "6. Collect static files"
    echo "7. Clean up (remove containers, networks, volumes)"
    echo "8. Check/Create Docker network (emc_network)"
    echo "9. Create Django superuser (admin)"
    echo "10. Initialize project data (init_project)"
    echo "0. Exit"
    echo -n "Choose an option: "
}

# Function to prune unused networks and volumes
cleanup() {
    echo -e "${RED}Cleaning up Docker...${RESET}"
    docker-compose down --volumes --remove-orphans
    docker network prune -f
    docker volume prune -f
}

# Function to check and create network
check_or_create_network() {
    if docker network ls | grep -q "emc_network"; then
        echo -e "${YELLOW}Network 'emc_network' already exists.${RESET}"
    else
        echo -e "${GREEN}Creating network 'emc_network'...${RESET}"
        docker network create emc_network
        echo -e "${GREEN}Network 'emc_network' created successfully.${RESET}"
    fi
}

# Function to run Django commands in the web container
run_django_command() {
    command=$1
    echo -e "${GREEN}Running Django command: ${command}${RESET}"
    docker compose run web python3 manage.py $command
}

# Menu loop
while true; do
    show_menu
    read -r option

    case $option in
    1) # Build all and start
        echo -e "${GREEN}Building all services...${RESET}"
        check_or_create_network
        docker compose build --no-cache
        docker compose up --remove-orphans -d
        echo -e "${GREEN}Running Django migrations and creating superuser...${RESET}"
        run_django_command makemigrations
        run_django_command migrate
        run_django_command "createsuperuser --username admin --email admin@example.com --noinput"
        echo -e "${YELLOW}Default superuser created (Username: admin, Password: 1).${RESET}"
        ;;
    2) # Build and start the web service
        echo -e "${GREEN}Building web service...${RESET}"
        docker compose build web
        docker compose up -d web
        ;;
    3) # Build and start the database service
        echo -e "${GREEN}Starting database service...${RESET}"
        docker compose up -d db
        ;;
    4) # Build and start the socket service
        echo -e "${GREEN}Building socket service...${RESET}"
        docker compose build socket
        docker compose up -d socket
        ;;
    5) # Run Django migrations
        echo -e "${GREEN}Running Django migrations...${RESET}"
        run_django_command makemigrations
        run_django_command migrate
        ;;
    6) # Collect static files
        echo -e "${GREEN}Collecting static files...${RESET}"
        run_django_command collectstatic --noinput
        ;;
    7) # Cleanup
        cleanup
        ;;
    8) # Check/Create Docker network
        check_or_create_network
        ;;
    9) # Create Django superuser
        echo -e "${GREEN}Creating Django superuser...${RESET}"
        run_django_command "createsuperuser --username admin --email admin@example.com --noinput"
        echo -e "${YELLOW}Default superuser created (Username: admin, Password: 1).${RESET}"
        ;;
    10) # Initialize project data
        echo -e "${GREEN}Initializing project data...${RESET}"
        run_django_command init_project
        ;;
    0) # Exit
        echo -e "${CYAN}Exiting setup script. Goodbye!${RESET}"
        break
        ;;
    *) # Invalid option
        echo -e "${RED}Invalid option. Try again.${RESET}"
        ;;
    esac
done
