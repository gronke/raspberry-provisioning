DOCUMENTATION = '''
---
module: confirm_device
short_description: User confirmation dialog before formatting SD-Card
description:
  - Ask user for target device name
  - Let user confirm device wipe
'''

EXAMPLES = '''
- name: ask for device and confirm
  action: confirm_device
'''