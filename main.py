from libprobe.probe import Probe
from lib.check.wireless import CheckWireless
from lib.check.memory import CheckMemory
from lib.check.packet import CheckPacket
from lib.check.connection import CheckConnection
from lib.check.bss import CheckBss
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = (
        CheckWireless,
        CheckMemory,
        CheckPacket,
        CheckConnection,
        CheckBss,
    )

    probe = Probe("merakiwireless", version, checks)

    probe.start()
