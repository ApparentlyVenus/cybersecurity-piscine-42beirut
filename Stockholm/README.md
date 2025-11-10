# Stockholm - Ransomware Simulation

A Python-based ransomware simulation tool for educational and testing purposes, designed to run in an isolated Docker environment.

## Features

- Encrypts files with common extensions using Fernet encryption
- Decrypts files with provided key
- Silent mode for automated testing
- Containerized environment for safe testing
- Auto-generates test files for demonstration
- Saves encryption key to `/app/stockholm.key` for recovery

## Quick Start

```bash
# Build and start the container
make up

# Access the container shell
make run

```

## Usage
``` bash
# Encrypt files in /root/infection
/app/Stockholm

# Encrypt silently (no output)
/app/Stockholm -s

# Decrypt files with key
/app/Stockholm -r <encryption_key>

# Show version
/app/Stockholm -v

```
## Cleanup Commands

``` bash
make build    # Build Docker image
make up       # Build and start container
make run      # Access container shell
make clean    # Stop and remove container
make fclean   # Full cleanup (container + image + host files)