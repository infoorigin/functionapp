# My Function App

## Overview

Azure Function App with multiple HTTP-triggered functions and a decoupled core for business logic.


## Setup

1. **Create Virtual Environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run Locally**
    ```bash
    func start
    ```

## Deployment

Deploy using Azure CLI:

```bash
az login
az functionapp create --resource-group <ResourceGroup> --consumption-plan-location <Location> \
    --runtime python --runtime-version 3.9 --functions-version 4 \
    --name <FunctionAppName> --storage-account <StorageAccount>
func azure functionapp publish <FunctionAppName>


