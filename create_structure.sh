#!/bin/bash

# Create directory structure
mkdir -p app/core app/db app/models app/schemas app/repositories app/services app/api/v1/endpoints
mkdir -p tests/integration tests/unit

# Create app files
touch app/__init__.py
touch app/main.py
touch app/core/__init__.py
touch app/core/config.py
touch app/core/exceptions.py
touch app/core/logging.py
touch app/db/__init__.py
touch app/db/session.py
touch app/models/__init__.py
touch app/models/device.py
touch app/models/telemetry.py
touch app/schemas/__init__.py
touch app/schemas/common.py
touch app/schemas/device.py
touch app/schemas/error.py
touch app/repositories/__init__.py
touch app/repositories/device_repository.py
touch app/services/__init__.py
touch app/services/device_service.py
touch app/api/__init__.py
touch app/api/deps.py
touch app/api/v1/__init__.py
touch app/api/v1/router.py
touch app/api/v1/endpoints/__init__.py
touch app/api/v1/endpoints/devices.py
touch app/api/v1/endpoints/health.py

# Create test files
touch tests/__init__.py
touch tests/conftest.py
touch tests/integration/__init__.py
touch tests/integration/test_devices_api.py
touch tests/unit/__init__.py
touch tests/unit/test_device_service.py

# Create root-level files
touch .env.example
touch .gitignore
touch pytest.ini
touch requirements.txt
touch README.md

echo "Project structure created successfully."
