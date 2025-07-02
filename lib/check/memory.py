import logging
import asyncio
import random
from typing import Any
from libprobe.asset import Asset
from libprobe.exceptions import CheckException, Severity
from ..query import query


async def get_memory(org_id: str, serial: str,
                     asset_config: dict) -> dict[str, Any]:
    req = (
        f'/organizations/{org_id}/devices/system/memory/usage/history/'
        f'byInterval?serials[]={serial}&interval=300&timespan=300')
    resp = await query(asset_config, req)
    if not isinstance(resp, dict) or len(resp.get('items', [])) == 0:
        raise Exception(
            'Memory usage history data for device with '
            f'serial `{serial}` not ready to query')
    memory = resp['items'][0]
    provisioned = memory["provisioned"]  # int?
    used = memory["used"]["median"]  # int?
    free = memory["free"]["median"]  # int?

    # All in kB, * 1000 -> bytes
    item = {
        "name": serial,
        "provisioned": None if provisioned is None else provisioned * 1000,
        "used": None if used is None else used * 1000,
        "free": None if free is None else free * 1000,
    }
    return item


async def check_memory(
        asset: Asset,
        asset_config: dict,
        config: dict) -> dict[str, list[dict[str, Any]]]:

    interval = config.get('_interval', 300)
    if interval != 300:
        logging.warning(
            f'Works best with a 5 minute interval but got '
            f'{interval} seconds interval for {asset}')

    org_id = config.get('id')
    if not org_id:
        raise Exception(
            'Missing organization ID in asset collector configuration')

    serial = config.get('serial')
    if not serial:
        raise Exception(
            'Missing Serial in asset collector configuration')

    try:
        item = await get_memory(org_id, serial, asset_config)
        assert item['provisioned'] is not None
        assert item['used'] is not None
        assert item['free'] is not None
    except Exception:
        await asyncio.sleep(16.0 + random.random()*5.0)  # Retry
        item = await get_memory(org_id, serial, asset_config)

    state = {
        "memory": [item],  # single item
    }
    return state
