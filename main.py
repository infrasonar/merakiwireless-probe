from libprobe.probe import Probe
from lib.check.device import check_device
from lib.check.bss import check_bss
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = {
        'device': check_device,
        'bss': check_bss,
    }

    probe = Probe("merakiwireless", version, checks)

    probe.start()
