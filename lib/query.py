import asyncio
import aiohttp
import os
from libprobe.exceptions import CheckException, Severity
from .connector import get_connector


max_requests = int(os.getenv('MAX_REQUESTS', '5'))
sem = asyncio.Semaphore(max_requests)


async def query(local_config: dict, req: str):
    api_key = local_config.get('secret')
    assert api_key, (
        'API key is missing, '
        'please provide the API key as `secret` in the appliance config')

    headers = {
        'X-Cisco-Meraki-API-Key': api_key,
    }
    uri = f'https://api.meraki.com/api/v1{req}'
    async with sem:
        async with aiohttp.ClientSession(connector=get_connector()) as session:
            async with session.get(uri, headers=headers, ssl=True) as resp:
                if resp.status == 429:
                    raise CheckException("(429) Too Many Requests",
                                         severity=Severity.LOW)
                assert resp.status // 100 == 2, (
                    f'response status code: {resp.status}; '
                    f'reason: {resp.reason}')

                data = await resp.json()
                return data
