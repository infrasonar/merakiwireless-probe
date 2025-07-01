import logging
from typing import Any
from libprobe.asset import Asset
from ..query import query


def _float(inp: float | int | str | None) -> float | None:
    return float(inp) if isinstance(inp, (int, str)) else inp


async def check_packet(
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
        f'/organizations/{org_id}/wireless/devices/packetLoss/'
        f'byDevice?timespan=300&serials[]={serial}')
    resp = await query(asset_config, req)
    if len(resp) == 0:
        raise Exception(
            'Packet loss for wireless '
            f'with serial `{serial}` not found')
    packet_loss = resp[0]
    items: list[dict[str, Any]] = []

    for stream in ('upstream', 'downstream'):
        data = packet_loss[stream]
        items.append({
            "name": stream,
            "total": data["total"],  # int
            "lost": data["lost"],  # int
            "lossPercentage": _float(data["lossPercentage"]),  # float?
        })

    state = {
        "loss": items,  # multiple (2) items
    }
    return state
