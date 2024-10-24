import httpx
import asyncio
from httpx import HTTPStatusError, RequestError

async def fetch_page(client, url, page, retries=3):
    """
    Fetch a single page of data with retries and exception handling.
    :param client: httpx.AsyncClient object
    :param url: API endpoint URL
    :param page: The page number to fetch
    :param retries: Number of retries on failure (default 3)
    :return: JSON response of the API call for the specific page
    """
    params = {'page': page}
    
    for attempt in range(1, retries + 1):
        try:
            response = await client.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()

        except HTTPStatusError as http_err:
            print(f"HTTP error on page {page}: {http_err}")
            if response.status_code == 404:
                print(f"Page {page} not found. Skipping.")
                return None  # Optionally skip the page if not found
            elif attempt == retries:
                raise  # Rethrow if all retries fail

        except RequestError as req_err:
            print(f"Network error on page {page}: {req_err}")
            if attempt == retries:
                raise  # Rethrow if all retries fail

        except Exception as e:
            print(f"Unexpected error on page {page}: {e}")
            if attempt == retries:
                raise  # Rethrow if all retries fail

        # Exponential backoff for retries
        await asyncio.sleep(2 ** attempt)

async def fetch_all_pages(url, total_pages, retries=3):
    """
    Fetch all pages of data in parallel with exception handling and retries.
    :param url: API endpoint URL
    :param total_pages: Total number of pages to fetch
    :param retries: Number of retries on failure (default 3)
    :return: Combined list of all pages' data
    """
    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_page(client, url, page, retries) for page in range(1, total_pages + 1)
        ]
        
        # Use asyncio.gather to fetch all pages concurrently
        pages_data = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine the results, skipping any None values from failed pages
        combined_data = []
        for page_data in pages_data:
            if isinstance(page_data, dict) and 'results' in page_data:
                combined_data.extend(page_data['results'])  # Assuming 'results' key holds data
            elif isinstance(page_data, Exception):
                print(f"Error occurred: {page_data}")

        return combined_data

async def get_paginated_data(url, total_pages, retries=3):
    """
    Fetch the paginated data by fetching all pages concurrently with retries.
    :param url: API endpoint URL
    :param total_pages: Total number of pages
    :param retries: Number of retries on failure (default 3)
    :return: Combined data from all pages
    """
    return await fetch_all_pages(url, total_pages, retries)

# To run the async function in a script
if __name__ == "__main__":
    url = "https://api.example.com/data"  # Replace with your actual API URL
    total_pages = 5  # Replace with the actual number of pages

    # Run the event loop to fetch paginated data with retries
    combined_data = asyncio.run(get_paginated_data(url, total_pages))
    print(combined_data)
