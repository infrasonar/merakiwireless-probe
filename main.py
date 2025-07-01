from libprobe.probe import Probe
from lib.check.wireless import check_wireless
from lib.check.memory import check_memory
from lib.check.packet import check_packet
from lib.check.connection import check_connection
from lib.check.bss import check_bss
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = {
        'wireless': check_wireless,
        'memory': check_memory,
        'packet': check_packet,
        'connection': check_connection,
        'bss': check_bss,
    }

    probe = Probe("merakiwireless", version, checks)

    probe.start()
