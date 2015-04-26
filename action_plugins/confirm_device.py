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


def convertSize(num, bsize=1024, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < bsize:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= bsize
    return "%.1f%s%s" % (num, 'Yi', suffix)

class ActionModule(object):

  def __init__(self, runner):
    #print MESSAGES['selectDisk']
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

  def get_disk_info(self, device):
    cmd = ['diskutil', 'info', '-plist', device]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE)
    (stdout, stderr) = p.communicate()
    try:
      plist = StringIO.StringIO(stdout)
      return plistlib.readPlist(plist)
    except ExpatError, emsg:
      raise DiskUtilError('Error parsing plist: %s' % stdout)

  def print_disk_info(self, disk):
    disk_info = self.get_disk_info(disk)
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
      disk = self.user_ask_disk()
      if(self.disk_exists(disk)):
        self.disk = disk
      else:
        print( "Error: %s is not a valid block device.\n" % disk )

    confirmed = self.user_ask_confirm()

    result = { 'disk': self.disk, 'confirmed': confirmed }

    return ReturnData(conn=conn, comm_ok=True, result=result)