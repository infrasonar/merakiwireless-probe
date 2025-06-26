import datetime
from typing import Any
from libprobe.asset import Asset
from ..query import query

# [
#   {
#     "name": "KAZ-HGC-AP1-5",
#     "serial": "Q3AC-2CM4-3YE8",
#     "mac": "0c:7b:c8:de:ef:f4",
#     "publicIp": "91.234.193.5",
#     "networkId": "N_676102894059038771",
#     "status": "online",
#     "lastReportedAt": "2025-06-26T11:43:27.061000Z",
#     "productType": "wireless",
#     "model": "MR46",
#     "tags": [],
#     "lanIp": "192.168.11.111",
#     "gateway": "192.168.11.1",
#     "ipType": "dhcp",
#     "primaryDns": "192.168.11.1",
#     "secondaryDns": null
#   }
# ]

async def get_status(org_id: str, serial: str) -> dict[str, Any]:
    pass


async def check_device(
        asset: Asset,
        asset_config: dict,
        config: dict) -> dict[str, list[dict[str, Any]]]:

    org_id = config.get('id')
    if not org_id:
        raise Exception(
            'Missing organization ID in asset collector configuration')

    serial = config.get('serial')
    if not serial:
        raise Exception(
            'Missing Serial in asset collector configuration')

    req = f'/organizations/1006940/devices?serials[]={serial}'
    resp = await query(asset, asset_config, asset_config, req)

    if len(resp) == 0:
        raise Exception(f'Device with serial `{serial}` not found')

    device = resp[0]

    try:
        datestr = device['configurationUpdatedAt']
        configuration_updated_at = \
            int(datetime.datetime.fromisoformat(datestr).timestamp())
    except Exception:
        configuration_updated_at = None

    details = device.get('details', [])
    running_software_version = None
    for detail in details:
        if detail.get('name') == 'Running software version':
            try:
                running_software_version = detail.get('value')
            except Exception:
                pass

    item = {
        "name": device['serial'],  # str
        "serial": device['serial'],  # str
        "deviceName": device['name'],  # str
        "mac": device['mac'],  # str
        "networkId": device['networkId'],  # str
        "productType": device['productType'],  # str
        "model": device['model'],  # str
        "address": device.get('address') or None,  # str?
        "lat": device['lat'],  # float
        "lng": device['lng'],  # float
        "notes": device.get('notes') or None,  # str?
        "configurationUpdatedAt": configuration_updated_at,  # int?
        "firmware": device['firmware'],  # str
        "running_software_version": running_software_version,  # str?
    }

    state = {
        "device": [item]
    }

    return state