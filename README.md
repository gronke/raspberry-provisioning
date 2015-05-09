Rarpberry Provisioning
======================

Toolchain to install and provision a Raspberry Pi headless.

This playbook collection consists of multiple steps that can be executed separately. Basically these are:

 * download and customize NOOBS image (local)
 * write image to SD card (local)
 * put SD card into RPI and wait for SSH to come up (human)
 * provision base system (network)

Setup
-----

### Dependencies

 * Mac OSX
 * Ansible
 * 2 GB local disk space
 * Raspberry PI (any version)
 * SD Card >= 4 GB
 * DHCP server

For now the SD Card preperation works on _OSX only_, because the SD Card format dialogs base on `diskutil`.

Please ensure you run this in a friendly network environment. For a few minutes during the installation your device will be accessible with default username/password combination.

### Configuration 

#### SSH Keys
Public RSA keys for SSH login are stored in the `config/ssh/authorized_keys/` directory each with `.pub` file extension.

Steps
-----

### Tweak NOOBS and flash image to SD-Card

```bash
ansible-playbook -i 127.0.0.1, create_sd_card.yml
```

The downloaded NOOBS image is cached in a `.tmp` directory to speed up future SD card creation. This directory is not necessary for further steps, so it can be deleted once the image customization is finished.

### Install Raspbian via NOOBS installer

The `write_sd_card.yml` Playbook will list your connected disks and ask for which to copy the custom NOOBS image to. Be careful, it will format all data on the device after asking your for confirmation.

```bash
ansible-playbook -i 127.0.0.1, write_sd_card.yml
```

### Install Raspbian with NOOBS headless installer

Once the NOOBS installer is copied to the SD card, it can be put into a Raspberry Pi with LAN connected. It will request an IP with DHCP, so that setting up a static lease for your Raspberry's MAC address.

This will take a few minutes. Once this task is finished the device will listen on `port 22` for SSH connections.

### Provision new created Raspbian base image over Network

After the headless install of Raspbian via NOOBS installer is finished it will start SSH on port 22. Simply put the IP address of your instance into your `Inventory` file:

```
[zombies]
192.168.1.23
```

After that the last step can be executed to do the initial configuration of your device (for example disabling the Raspbian installer you could have noticed after booting when the RPI is connected to a screen).

```bash
ansible-playbook -i Inventory provision_zombies.yml
```
