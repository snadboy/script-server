FROM python:3.9-slim

# Set bash as default shell (required for devcontainer features)
SHELL ["/bin/bash", "-c"]

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Install Python dependencies inline (avoids context issues)
RUN pip install --no-cache-dir tornado>=4 bcrypt>=4.0.0

# Create non-root user (required for devcontainer features)
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

USER $USERNAME
