import subprocess
import shlex
import json
from functools import total_ordering
import tabulate


@total_ordering
class Device:
    def __init__(self, data: dict):
        self._data = data

    def __eq__(self, other):
        return self.wwn == other.wwn

    def __lt__(self, other):
        return self.name < other.name and len(self.name) <= len(other.name)

    def __str__(self):
        return ' '.join(self._display_fields)

    def __iter__(self):
        return (x for x in self._display_fields)

    @property
    def _display_fields(self):
        return [self.path, self.wwn_path, self.model, self.size]

    @property
    def device_type(self):
        return self._data['type']

    @property
    def hctl(self):
        return self._data['hctl']

    @property
    def model(self):
        return self._data['model']

    @property
    def name(self):
        return self._data['name']

    @property
    def path(self):
        return self._data['path']

    @property
    def revision(self):
        return self._data['rev']

    @property
    def size(self):
        return self._data['size']

    @property
    def tran(self):
        return self._data['tran']

    @property
    def vendor(self):
        return self._data['vendor']

    @property
    def wwn(self):
        return self._data['wwn']

    @property
    def wwn_path(self):
        if self.tran == 'sas':
            return f'/dev/disk/by-id/wwn-{self.wwn}'
        elif self.tran == 'nvme':
            return f'/dev/disk/by-id/nvme-{self.wwn}'


def get_zpool_devices():
    p = subprocess.Popen(shlex.split('zpool status'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    assert p.returncode == 0
    s = out.decode().strip()


def main():
    p = subprocess.Popen(shlex.split('lsblk -O -d -J'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    assert p.returncode == 0
    s = out.decode().strip()
    obj = json.loads(s)['blockdevices']
    devices = sorted([Device(x) for x in obj])
    print(tabulate.tabulate(devices, tablefmt='plain'))


if __name__ == '__main__':
    main()