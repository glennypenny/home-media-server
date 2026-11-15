# 03 — Samba

Samba runs natively on the host (not in Docker) and exposes a single directory
as a network share: `/srv/samba/share/sambashare`.

## Install

    sudo apt install samba

## Shared directory

    sudo mkdir -p /srv/samba/share/sambashare
    sudo mkdir -p /srv/samba/share/sambashare/movies
    sudo mkdir -p /srv/samba/share/sambashare/tv

Owned by the local user; no separate group. Permissions are handled by Samba
based on the authenticated user.

## Configuration

Created as a usershare through the Ubuntu GUI (Settings → Sharing), which
writes to `/var/lib/samba/usershares/` rather than `/etc/samba/smb.conf`.

The effective result, as shown by `testparm -s`:

    [sambashare]
        comment = Samba on Ubuntu
        create mask = 0664
        directory mask = 0775
        path = /srv/samba/share/sambashare
        read only = No
        valid users = glen
        write list = glen

A sanitised copy is in `samba/smb.conf.example` for reference.

## Usershare caveat

Usershares are created and owned by a specific user. They apply to that user's
`smb.conf` view and are stored separately from the system config. If the user
is renamed, removed, or permissions are disturbed, the share disappears from
`testparm` output even though the file in `usershares/` still exists.

For a more portable setup, the same share could be added directly to
`/etc/samba/smb.conf`. The current setup uses usershares because that is what
the GUI produced, and it works.

## Samba password

    sudo smbpasswd -a glen

This password is separate from the Linux login password; it's only used for
SMB authentication.

## Access from other machines

- Windows: `\\192.168.28.11\sambashare`
- macOS: Finder → Go → Connect to Server → `smb://192.168.28.11/sambashare`
- Linux: `smb://192.168.28.11/sambashare` in a file manager, or
  `smbclient //192.168.28.11/sambashare -U glen`

## Reload after config changes

    sudo systemctl reload smbd
