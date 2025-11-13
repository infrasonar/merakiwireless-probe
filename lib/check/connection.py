import logging
from libprobe.asset import Asset
from libprobe.check import Check
from ..query import query


class CheckConnection(Check):
    key = 'connection'
    unchanged_eol = 14400

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

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
        resp = await query(local_config, req)
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
