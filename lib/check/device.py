import asyncio
import datetime
import logging
from typing import Any
from libprobe.asset import Asset
from ..query import query


def _float(inp: float | int | str | None) -> float | None:
    return float(inp) if isinstance(inp, (int, str)) else inp


async def update_status(org_id: str, serial: str,
                        asset_config: dict[str, Any],
                        item: dict[str, Any]):
    req = f'/organizations/{org_id}/devices/statuses?serials[]={serial}'
    resp = await query(asset_config, req)
    if len(resp) == 0:
        raise Exception(f'Device status with serial `{serial}` not found')

    status = resp[0]

    try:
        datestr = status['lastReportedAt']
        last_reported_at = \
            int(datetime.datetime.fromisoformat(datestr).timestamp())
    except Exception:
        last_reported_at = None

    item["status"] = status['status']  # str
    item["lastReportedAt"] = last_reported_at  # int?
    item["lanIp"] = status.get('lanIp') or None  # str?
    item["gateway"] = status.get('gateway') or None  # str?
    item["ipType"] = status.get('ipType') or None  # str?
    item["primaryDns"] = status.get('primaryDns') or None  # str?
    item["secondaryDns"] = status.get('secondaryDns') or None  # str?


async def update_mem_perf(org_id: str, serial: str,
                          asset_config: dict[str, Any],
                          item: dict[str, Any]):
    req = (
        f'/organizations/{org_id}/devices/system/memory/usage/history/'
        f'byInterval?serials[]={serial}&interval=300&timespan=300')
    resp = await query(asset_config, req)
    if not isinstance(resp, dict) or len(resp.get('items', [])) == 0:
        raise Exception(f'Memory history for serial `{serial}` not found')
    memory = resp['items'][0]

    # All in kB, * 1000 -> bytes
    item['memoryProvisioned'] = memory["provisioned"] * 1000  # int
    item['memoryUsed'] = memory["used"]["median"] * 1000  # int
    item['memoryFree'] = memory["free"]["median"] * 1000  # int


async def update_packet_loss(org_id: str, serial: str,
                             asset_config: dict[str, Any],
                             item: dict[str, Any]):
    req = (
        f'/organizations/{org_id}/wireless/devices/packetLoss/'
        f'byDevice?serials[]={serial}')
    resp = await query(asset_config, req)
    if len(resp) == 0:
        raise Exception(
            'Packet loss for wireless '
            f'with serial `{serial}` not found')
    packet_loss = resp[0]
    for stream in ('upstream', 'downstream'):
        data = packet_loss[stream]
        item[f'{stream}Total'] = data["total"]  # int
        item[f'{stream}Lost'] = data["lost"]  # int
        item[f'{stream}LossPercentage'] = \
            _float(data["lossPercentage"])  # float


async def update_signal_quality(network_id: str, serial: str,
                                asset_config: dict[str, Any],
                                item: dict[str, Any]):
    req = (
        f'networks/{network_id}/wireless/signalQualityHistory'
        f'?timespan=300&resolution=300&deviceSerial={serial}')
    resp = await query(asset_config, req)
    if len(resp) == 0:
        raise Exception(
            'Signal strength for wireless '
            f'with serial `{serial}` not found')
    signal_quality = resp[0]
    item["signalQualitySnr"] = signal_quality['snr']  # int  (e.g. 39)
    item["signalQualityRssi"] = signal_quality['rssi']  # int  (e.g. -59)


async def update_latency(network_id: str, serial: str,
                         asset_config: dict[str, Any],
                         item: dict[str, Any]):
    req = (
        f'networks/{network_id}/wireless/latencyHistory'
        f'?timespan=300&resolution=300&deviceSerial={serial}')
    resp = await query(asset_config, req)
    if len(resp) == 0:
        raise Exception(
            'Signal strength for wireless '
            f'with serial `{serial}` not found')
    latency = resp[0]
    item["avgLatencyMs"] = latency['avgLatencyMs']  # int


async def update_rate(network_id: str, serial: str,
                      asset_config: dict[str, Any],
                      item: dict[str, Any]):
    req = (
        f'networks/{network_id}/wireless/dataRateHistory'
        f'?timespan=300&resolution=300&deviceSerial={serial}')
    resp = await query(asset_config, req)
    if len(resp) == 0:
        raise Exception(
            'Data rate for wireless '
            f'with serial `{serial}` not found')
    rate = resp[0]
    # Kbps -> bytes per second
    item["averageBps"] = rate['averageKbps'] * 125  # int
    item["downloadBps"] = rate['downloadKbps'] * 125  # int
    item["uploadBps"] = rate['uploadKbps'] * 125  # int


async def update_client_count(network_id: str, serial: str,
                              asset_config: dict[str, Any],
                              item: dict[str, Any]):
    req = (
        f'networks/{network_id}/wireless/clientCountHistory'
        f'?timespan=300&resolution=300&deviceSerial={serial}')
    resp = await query(asset_config, req)
    if len(resp) == 0:
        raise Exception(
            'Client count for wireless '
            f'with serial `{serial}` not found')
    client_count = resp[0]
    item["clientCount"] = client_count['clientCount']  # int


async def update_connection_stats(serial: str,
                                  asset_config: dict[str, Any],
                                  item: dict[str, Any]):
    req = f'devices/{serial}/wireless/connectionStats?timespan=300'
    resp = await query(asset_config, req)
    if len(resp) == 0:
        raise Exception(
            'Connection stats for wireless '
            f'with serial `{serial}` not found')
    connection_stats = resp['connectionStats']
    item["connectionStatsAssoc"] = connection_stats['assoc']  # int
    item["connectionStatsAuth"] = connection_stats['auth']  # int
    item["connectionStatsDhcp"] = connection_stats['dhcp']  # int
    item["connectionStatsDns"] = connection_stats['dns']  # int
    item["connectionStatsSuccess"] = connection_stats['success']  # int


async def get_channel_utilization(org_id: str, serial: str,
                                  asset_config: dict[str, Any]
                                  ) -> list[dict[str, Any]]:
    req = (
        f'/organizations/{org_id}/wireless/devices/channelUtilization/'
        f'byDevice?interval=300&timespan=300&serials[]={serial}')
    resp = await query(asset_config, req)
    if len(resp) == 0:
        raise Exception(
            'Channel utilization for wireless '
            f'with serial `{serial}` not found')
    channel_utilization = resp[0]
    by_band = channel_utilization.get('byBand', [])
    items: list[dict[str, Any]] = []
    for band in by_band:
        items.append({
            "name": band["band"],  # str, e.g. "2.4"
            "serial": serial,
            "wifiPercentage": float(band["wifi"]["percentage"]),  # float
            "nonWifiPercentage": float(band["nonWifi"]["percentage"]),  # float
            "totalPercentage": float(band["total"]["percentage"]),  # float
        })
    return items


async def check_device(
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

    req = f'/organizations/{org_id}/devices?serials[]={serial}'
    resp = await query(asset_config, req)

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

    name = device['serial']
    network_id = device['networkId']
    item = {
        "name": name,  # str (serial)
        "deviceName": device['name'],  # str
        "mac": device['mac'],  # str
        "networkId": network_id,  # str
        "productType": device['productType'],  # str
        "model": device['model'],  # str
        "address": device.get('address') or None,  # str?
        "lat": float(device['lat']),  # float
        "lng": float(device['lng']),  # float
        "notes": device.get('notes') or None,  # str?
        "configurationUpdatedAt": configuration_updated_at,  # int?
        "firmware": device['firmware'],  # str
        "runningSoftwareVersion": running_software_version,  # str?
    }
    await update_status(org_id, serial, asset_config, item)

    try:
        await update_mem_perf(org_id, serial, asset_config, item)
    except Exception:
        await asyncio.sleep(1.0)  # retry
        await update_mem_perf(org_id, serial, asset_config, item)

    try:
        await update_packet_loss(org_id, serial, asset_config, item)
    except Exception:
        await asyncio.sleep(1.0)  # retry
        await update_packet_loss(org_id, serial, asset_config, item)

    try:
        await update_signal_quality(network_id, serial, asset_config, item)
    except Exception:
        await asyncio.sleep(1.0)  # retry
        await update_signal_quality(network_id, serial, asset_config, item)

    try:
        await update_latency(network_id, serial, asset_config, item)
    except Exception:
        await asyncio.sleep(1.0)  # retry
        await update_latency(network_id, serial, asset_config, item)

    try:
        await update_rate(network_id, serial, asset_config, item)
    except Exception:
        await asyncio.sleep(1.0)  # retry
        await update_rate(network_id, serial, asset_config, item)

    try:
        await update_client_count(network_id, serial, asset_config, item)
    except Exception:
        await asyncio.sleep(1.0)  # retry
        await update_client_count(network_id, serial, asset_config, item)

    try:
        await update_connection_stats(serial, asset_config, item)
    except Exception:
        await asyncio.sleep(1.0)  # retry
        await update_connection_stats(serial, asset_config, item)

    try:
        channel_utilization = \
            await get_channel_utilization(org_id, serial, asset_config)
    except Exception:
        await asyncio.sleep(1.0)  # retry
        channel_utilization = \
            await get_channel_utilization(org_id, serial, asset_config)

    state = {
        "device": [item],  # single item
        "channelUtilization": channel_utilization,  # multi items
    }

    return state
