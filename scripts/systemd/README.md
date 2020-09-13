This is a simple systemd service for `AntEye`

# Installation

Replace `/root/AntEye` with the location of your `AntEye` installation (two instances in the file)

Start the service

```
systemctl start AntEye.service
systemctl status AntEye.service
```

If everything looks good, enable a startup upon reboot

```
systemctl enable AntEye.service
```
