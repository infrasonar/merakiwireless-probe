import logging
from typing import Any
from libprobe.asset import Asset
from ..query import query


async def check_connection(
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

    req = f'/devices/{serial}/wireless/connectionStats?timespan=300'
    resp = await query(asset_config, req)
    if len(resp) == 0:
        raise Exception(
            'Connection stats for wireless '
            f'with serial `{serial}` not found')
    connection_stats = resp['connectionStats']
    item = {
        "name": serial,
        "assoc": connection_stats['assoc'],  # int
        "auth": connection_stats['auth'],  # int
        "dhcp": connection_stats['dhcp'],  # int
        "dns": connection_stats['dns'],  # int
        "success": connection_stats['success'],  # int
    }

    state = {
        "stats": [item],  # single item
    }
    return state
