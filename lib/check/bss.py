from typing import Any
from libprobe.asset import Asset
from ..query import query


async def check_bss(
        asset: Asset,
        asset_config: dict,
        config: dict) -> dict[str, list[dict[str, Any]]]:
    serial = config.get('serial')
    if not serial:
        raise Exception(
            'Missing Serial in asset collector configuration')

    req = f'/devices/{serial}/wireless/status'
    resp = await query(asset_config, req)

    bss = resp.get('basicServiceSets')
    if not isinstance(bss, (list, tuple)):
        raise Exception(f'Basic Service Sets for serial `{serial}` not found')

    items: list[dict[str, Any]] = []
    for item in bss:
        items.append({
            "name": item["bssid"],  # str
            "ssidName": item["ssidName"],  # str
            "ssidNumber": item["ssidNumber"],  # int
            "enabled": item["enabled"],  # bool
            "band": item["band"],  # str
            "channel": item["channel"],  # int
            "channelWidth": item["channelWidth"],  # str
            "power": item["power"],  # str
            "visible": item["visible"],  # bool
            "broadcasting": item["broadcasting"],  # bool
        })

    state = {
        "basicServiceSets": items
    }

    return state
