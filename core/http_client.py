import httpx
import asyncio
from httpx import HTTPStatusError, RequestError
from typing import Any, Dict, List

class HttpClient:
    def __init__(self, retries=3, timeout=10):
        """
        Initialize the HttpClient with retry and timeout settings.
        :param retries: Number of retries on failure (default 3)
        :param timeout: Request timeout in seconds (default 10)
        """
        self.retries = retries
        self.timeout = timeout
        
    def create_batches(total_records, batch_size):
        # List to hold the batch dictionaries
        batches = []
        
        # Loop through the total_records with the given batch size
        for offset in range(0, total_records, batch_size):
            batch = {
                "limit": batch_size,
                "offset": offset
            }
            batches.append(batch)
        
        return batches
        
    async def fetch(self, client, request_config):
        """
        Fetch data for a single request configuration with retries and exception handling.
        :param client: httpx.AsyncClient object
        :param request_config: Dictionary containing request parameters
            Expected keys: 'method', 'url', 'params', 'headers', 'data', 'json', 'id'
        :return: JSON response of the API call
        """
        method = request_config.get('method', 'GET').upper()
        url = request_config['url']
        params = request_config.get('params', {})
        headers = request_config.get('headers', {})
        data = request_config.get('data', None)
        json_data = request_config.get('json', None)
        identifier = request_config.get('id', url)  # An identifier for logging

        for attempt in range(1, self.retries + 1):
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    headers=headers,
                    data=data,
                    json=json_data,
                    timeout=self.timeout
                )
                response.raise_for_status()  # Raise an exception for HTTP errors
                return response.json()

            except HTTPStatusError as http_err:
                print(f"HTTP error on request {identifier}: {http_err}")
                if response.status_code == 404:
                    print(f"Resource not found for request {identifier}. Skipping.")
                    return None  # Optionally skip if not found
                elif attempt == self.retries:
                    raise  # Rethrow if all retries fail

            except RequestError as req_err:
                print(f"Network error on request {identifier}: {req_err}")
                if attempt == self.retries:
                    raise  # Rethrow if all retries fail

            except Exception as e:
                print(f"Unexpected error on request {identifier}: {e}")
                if attempt == self.retries:
                    raise  # Rethrow if all retries fail

            # Exponential backoff for retries
            await asyncio.sleep(2 ** attempt)

    async def fetch_all(self, requests_list):
        """
        Fetch all requests in parallel.
        :param requests_list: List of request configuration dictionaries
        :return: List of responses from all requests
        """
        async with httpx.AsyncClient() as client:
            tasks = [
                self.fetch(client, request_config) for request_config in requests_list
            ]

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            results = []
            for response in responses:
                if isinstance(response, dict):
                    results.append(response)
                elif isinstance(response, Exception):
                    print(f"Error occurred: {response}")
                    # Optionally, append None or handle the exception as needed
                    results.append(None)
                else:
                    # In case the response is None or any other type
                    results.append(response)

            return results

    async def get_parallel_data(self, request_config):
        """
        Fetch data from multiple requests in parallel.
        :param request_config: An instance of RequestConfig Pydantic model
        :return: List of responses from all requests
        """
        requests_list = []
        baseUrl = request_config.baseUrl
        method = request_config.method
        headers = request_config.headers
        global_id = request_config.id

        for item in request_config.inputData:
            placeholders = item.placeholders
            params = item.params  # Now params is a dict

            # Replace placeholders in baseUrl
            try:
                url = baseUrl.format(**placeholders)
            except KeyError as e:
                print(f"Missing placeholder {e} in baseUrl.")
                continue  # Skip this item or handle as needed

            # Build the request configuration
            req_config = {
                'method': method,
                'url': url,
                'params': params,
                'headers': headers,
                'id': f"{global_id}-{placeholders.get('id', '')}"
            }
            requests_list.append(req_config)

        return await self.fetch_all(requests_list)
