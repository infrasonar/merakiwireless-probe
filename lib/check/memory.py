import logging
from typing import Any
from libprobe.asset import Asset
from ..query import query


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

    req = (
        f'/organizations/{org_id}/devices/system/memory/usage/history/'
        f'byInterval?serials[]={serial}&interval=300&timespan=300')
    resp = await query(asset_config, req)
    if not isinstance(resp, dict) or len(resp.get('items', [])) == 0:
        raise Exception(f'Memory history for serial `{serial}` not found')
    memory = resp['items'][0]

    # All in kB, * 1000 -> bytes
    item = {
        "name": serial,
        "provisioned": memory["provisioned"] * 1000,  # int
        "used": memory["used"]["median"] * 1000,  # int
        "free": memory["free"]["median"] * 1000,  # int
    }

    state = {
        "memory": [item],  # single item
    }
    return state
