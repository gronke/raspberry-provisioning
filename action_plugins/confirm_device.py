#!/usr/bin/env python
import os
import math
import pipes
import stat
import plistlib
import StringIO
from ansible import utils
from ansible import errors
from ansible.runner.return_data import ReturnData
from subprocess import Popen, PIPE
from xml.parsers.expat import ExpatError

MESSAGES = {
  'selectDisk': 'Please enter the device name of your SD-Card: ',
  'confirm': 'Are you sure to delete this disk? (no/yes) ',
  'diskInfo': 'The device %s will be deleted (%s)'
}

PARTITION_NAME = 'NOOBS'
PARTITION_FILESYSTEM = 'FAT32'
PARTITION_INDEX_TYPE = 'MBR'

def convertSize(num, bsize=1024, suffix='B'):
  for unit in ['','K','M','G','T','P','E','Z']:
      if abs(num) < bsize:
          return "%3.1f%s%s" % (num, unit, suffix)
      num /= bsize
  return "%.1f%s%s" % (num, 'Yi', suffix)

def format_disk(disk):
  size = convertSize(get_device_info(disk).TotalSize, 1000)
  cmd = ['diskutil', 'partitionDisk', disk, PARTITION_INDEX_TYPE, PARTITION_FILESYSTEM, PARTITION_NAME, size];
  p = Popen(cmd, stdin=PIPE, stdout=PIPE)
  (stdout, stderr) = p.communicate()
  return '/dev/' + get_device_info(disk).DeviceIdentifier + 's1';

def get_device_info(device):
  cmd = ['diskutil', 'info', '-plist', device]
  p = Popen(cmd, stdin=PIPE, stdout=PIPE)
  (stdout, stderr) = p.communicate()
  try:
    plist = StringIO.StringIO(stdout)
    return plistlib.readPlist(plist)
  except ExpatError, emsg:
    raise DiskUtilError('Error parsing plist: %s' % stdout)

class ActionModule(object):

  def __init__(self, runner):
    self.runner = runner
    self.disk = None

  def _prompt(self, message):
    prompt = MESSAGES[message]
    res = raw_input(prompt)
    return res

  def disk_exists(self, disk):
    try:
      mode = os.lstat(disk).st_mode
    except OSError:
      return False
    else: 
      return stat.S_ISBLK(mode)

  def print_disks(self):
    cmd = ['diskutil', 'list']
    p = Popen(cmd, stdin=PIPE, stdout=PIPE)
    (stdout, stderr) = p.communicate()
    print(stdout)

  def print_disk_info(self, disk):
    disk_info = get_device_info(disk)
    print ''
    print MESSAGES['diskInfo'] % (disk, convertSize(disk_info.TotalSize, 1000))

  def user_ask_disk(self):
    disk = self._prompt('selectDisk')
    return disk

  def user_ask_confirm(self):
    self.print_disk_info(self.disk)
    confirm = self._prompt('confirm')
    return confirm == 'yes'

  def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):

    self.print_disks()
    while(self.disk is None):
      #disk = self.user_ask_disk()
      disk = '/dev/disk2'
      if(self.disk_exists(disk)):
        self.disk = disk
      else:
        print( "Error: %s is not a valid block device.\n" % disk )

    confirmed = self.user_ask_confirm()

    result = { 'disk': self.disk, 'confirmed': confirmed }

    if(confirmed):
      partition_identifier = format_disk(self.disk);
      result['partition'] = get_device_info(partition_identifier)

    return ReturnData(conn=conn, comm_ok=True, result=result)
