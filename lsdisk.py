import json
import os
import shlex
import subprocess
import sys
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
        return [self.path, self.wwn_path, self.model, self.size, self.ss, self.associated_array_fstype, self.associated_array_label]

    @property
    def _children(self):
        try:
            return self._data['children']
        except KeyError:
            return []

    @property
    def children(self):
        return [Device(x) for x in self._children]

    @property
    def device_type(self):
        return self._data['type']

    @property
    def fstype(self):
        return self._data['fstype'] or ''

    @property
    def hctl(self):
        return self._data['hctl']

    @property
    def label(self):
        return self._data['label']

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
    def sl(self):
        return self._data['log-sec']
    
    @property
    def sp(self):
        return self._data['phy-sec']
    
    @property
    def ss(self):
        return '{}/{}'.format(self.sl, self.sp)

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

    @property
    def associated_array_fstype(self):
        if self.fstype:
            return self.fstype

        for s in map(lambda d: d.fstype if '_member' in d.fstype else None, self.children):
            if s:
                return s

    @property
    def associated_array_label(self):
        if self.label:
            return self.label

        for label in map(lambda d: d.label if '_member' in d.fstype else None, self.children):
            if label:
                return label


def get_zpool_devices():
    p = subprocess.Popen(shlex.split('zpool status'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    assert p.returncode == 0
    s = out.decode().strip().split('\n')

    # parse


def main():
    p = subprocess.Popen(shlex.split('lsblk -O -J'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    assert p.returncode == 0
    s = out.decode().strip()
    obj = json.loads(s)['blockdevices']
    devices = sorted([Device(x) for x in obj])

    if os.isatty(sys.stdout.fileno()):
        tablefmt = 'psql'
    else:
        tablefmt = 'plain'
    print(tabulate.tabulate(devices, tablefmt=tablefmt))


if __name__ == '__main__':
    main()
