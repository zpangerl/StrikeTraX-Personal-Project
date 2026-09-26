# Base image
FROM python:3.12-slim-bookworm

# Got off google.
# Need curl in order to download the microsoft driver config file.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install the Microsoft ODBC Driver 18 for SQL Server + unixODBC dev headers, from
# https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver17
RUN curl -sSL -O https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && apt-get install -y unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv. From:
# https://docs.astral.sh/uv/guides/integration/docker/
COPY --from=ghcr.io/astral-sh/uv:0.12.19 /uv /uvx /bin/

WORKDIR /app

# Exclude dev only dependencies, app doesn't need them.
ENV UV_NO_DEV=1

# Copy dependency files and install dependencies.
# Will almost never change, separate from application code.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

# Copy application code and sync.
COPY . .
RUN uv sync --locked

# Azure App Service defaults to port 80.
EXPOSE 80

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
