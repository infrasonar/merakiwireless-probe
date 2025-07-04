import asyncio
import datetime
import logging
import random
from typing import Any
from libprobe.asset import Asset
from libprobe.exceptions import CheckException, Severity
from ..query import query


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


async def get_signal_quality(network_id: str, serial: str,
                             asset_config: dict[str, Any]):
    req = (
        f'/networks/{network_id}/wireless/signalQualityHistory'
        f'?timespan=300&resolution=300&deviceSerial={serial}')
    resp = await query(asset_config, req)
    if len(resp) == 0:
        raise CheckException(
            'Signal strength history data for wireless with '
            f'serial `{serial}` not ready to query', severity=Severity.LOW)
    signal_quality = resp[0]
    return {
        "name": serial,
        "networkId": network_id,
        "snr": signal_quality['snr'],  # int?  (e.g. 39)
        "rssi": signal_quality['rssi'],  # int?  (e.g. -59)
    }


async def update_latency(network_id: str, serial: str,
                         asset_config: dict[str, Any],
                         item: dict[str, Any]):
    req = (
        f'/networks/{network_id}/wireless/latencyHistory'
        f'?timespan=300&resolution=300&deviceSerial={serial}')
    resp = await query(asset_config, req)
    if len(resp) == 0:
        raise CheckException(
            'Signal strength history data for wireless with '
            f'serial `{serial}` not ready to query', severity=Severity.LOW)
    latency = resp[0]
    item["avgLatencyMs"] = latency['avgLatencyMs']  # int?


async def update_rate(network_id: str, serial: str,
                      asset_config: dict[str, Any],
                      item: dict[str, Any]):
    req = (
        f'/networks/{network_id}/wireless/dataRateHistory'
        f'?timespan=300&resolution=300&deviceSerial={serial}')
    resp = await query(asset_config, req)
    if len(resp) == 0:
        raise CheckException(
            'Data rate history for wireless with '
            f'serial `{serial}` not ready to query', severity=Severity.LOW)
    rate = resp[0]
    averageKbps = rate['averageKbps']  # int?
    downloadKbps = rate['downloadKbps']  # int?
    uploadKbps = rate['uploadKbps']  # int?

    # Kbps -> bytes per second
    item["averageBps"] = None if averageKbps is None else averageKbps * 125
    item["downloadBps"] = None if downloadKbps is None else downloadKbps * 125
    item["uploadBps"] = None if uploadKbps is None else uploadKbps * 125


async def update_client_count(network_id: str, serial: str,
                              asset_config: dict[str, Any],
                              item: dict[str, Any]):
    req = (
        f'/networks/{network_id}/wireless/clientCountHistory'
        f'?timespan=300&resolution=300&deviceSerial={serial}')
    resp = await query(asset_config, req)
    if len(resp) == 0:
        raise CheckException(
            'Client count history data for wireless with '
            f'serial `{serial}` not ready to query', severity=Severity.LOW)
    client_count = resp[0]
    item["clientCount"] = client_count['clientCount']  # int?


async def get_channel_utilization(org_id: str, serial: str,
                                  asset_config: dict[str, Any]
                                  ) -> list[dict[str, Any]]:
    req = (
        f'/organizations/{org_id}/wireless/devices/channelUtilization/'
        f'byDevice?interval=300&timespan=300&serials[]={serial}')
    resp = await query(asset_config, req)
    if len(resp) == 0:
        raise CheckException(
            'Channel utilization data for wireless with '
            f'serial `{serial}` not ready to query', severity=Severity.LOW)
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


async def check_wireless(
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

    network_id = device['networkId']
    item = {
        "name": serial,  # str (serial)
        "organizationId": org_id,
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

    network = {
        "name": serial,
        "networkId": network_id,
    }

    try:
        await update_latency(network_id, serial, asset_config, network)
        assert network["avgLatencyMs"] is not None
    except Exception:
        await asyncio.sleep(16.0 + random.random()*5.0)  # Retry
        await update_latency(network_id, serial, asset_config, network)

    try:
        await update_rate(network_id, serial, asset_config, network)
        assert network["averageBps"] is not None
        assert network["downloadBps"] is not None
        assert network["uploadBps"] is not None
    except Exception:
        await asyncio.sleep(16.0 + random.random()*5.0)  # Retry
        await update_rate(network_id, serial, asset_config, network)

    try:
        await update_client_count(network_id, serial, asset_config, network)
        assert network["clientCount"] is not None
    except Exception:
        await asyncio.sleep(16.0 + random.random()*5.0)  # Retry
        await update_client_count(network_id, serial, asset_config, network)

    try:
        signal_quality = \
            await get_signal_quality(network_id, serial, asset_config)
        assert signal_quality["snr"] is not None
        assert signal_quality["rssi"] is not None
    except Exception:
        await asyncio.sleep(16.0 + random.random()*5.0)  # Retry
        signal_quality = \
            await get_signal_quality(network_id, serial, asset_config)

    try:
        channel_utilization = \
            await get_channel_utilization(org_id, serial, asset_config)
    except Exception:
        await asyncio.sleep(16.0 + random.random()*5.0)  # Retry
        channel_utilization = \
            await get_channel_utilization(org_id, serial, asset_config)

    state = {
        "device": [item],  # single item
        "network": [network],  # single item
        "signalQuality": [signal_quality],  # single item
        "channelUtilization": channel_utilization,  # multi items
    }

    return state
