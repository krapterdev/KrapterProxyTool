# Krapter Proxy Tool

A powerful proxy scraping and checking tool with a modern dashboard.

## Features

- **Proxy Scraping**: Scrapes proxies from multiple sources.
- **Proxy Checking**: Validates proxies and categorizes them by speed (Gold, Silver, Bronze).
- **Dashboard**: Real-time dashboard to monitor proxy status.
- **Stability Score**: Visual indicator of proxy stability.
- **Country Flags**: Displays country of origin for each proxy.

## Installation & Usage (Docker)

The application is containerized using Docker. This ensures all dependencies (PostgreSQL, Redis, Python) are set up correctly.

### Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux/Ubuntu)
- **Docker Compose**

### How to Run

1.  Clone the repository:

    ```bash
    git clone <your-repo-url>
    cd KrapterProxyTool
    ```

2.  Run with Docker Compose:

    **Windows / Mac / Newer Linux:**

    ```bash
    docker compose up --build
    ```

    **Ubuntu (Legacy/Standard):**

    ```bash
    docker-compose up --build
    ```

    _If `docker-compose` is not found on Ubuntu, install it:_

    ```bash
    sudo apt-get update
    sudo apt-get install docker-compose-plugin
    # Then use: docker compose up --build
    ```

3.  Access the Dashboard:
    - Open `http://localhost:8080` in your browser.
    - **Login**: `krapter.dev@gmail.com` / `admin123`

### Troubleshooting

- **"Connection Refused"**: Ensure you are running with Docker, not `python start.py`.
- **"No Proxies"**: Check the Docker logs. The worker might be failing to fetch from sources if the container has no internet access.
