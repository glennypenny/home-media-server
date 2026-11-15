# 01 — Operating system

## The plan and the pivot

The original plan was **Ubuntu Server 24.04 LTS**: headless from the start,
no GUI, minimal surface area. That's the standard recommendation for a home
server.

In practice, Ubuntu Server's installer repeatedly failed on this hardware, and
its Wi-Fi driver support was not workable on the Omen 15. Wi-Fi is the only
network interface available on this laptop, so a server install without working
Wi-Fi is useless.

The pivot was to **Ubuntu Desktop 24.04 LTS**. The graphical installer handled
Wi-Fi configuration without issue. Once installed and connected, the GUI was
disabled so the system runs headless in practice.

## Disabling the GUI

sudo systemctl set-default multi-user.target
sudo reboot

After reboot, the system boots to a TTY login instead of a graphical session.
The GUI packages remain installed; they are simply not started. To temporarily
start a graphical session, use sudo systemctl start gdm3 (or lightdm, if
that is the display manager in use).

## Why this is a valid choice

"Use Ubuntu Server, not Desktop" is common advice, but it assumes the hardware
is supported. When Server's installer or drivers fail, Desktop is a legitimate
fallback — it is the same OS with a graphical session on top. Disabling the GUI
achieves most of the same result (less RAM idle, fewer services running) with
the setup friction removed.

The remaining difference is cosmetic: Desktop ships more packages, so the
attack surface is marginally larger. On a LAN-only server this is acceptable.

## Result

- Ubuntu 24.04.5 LTS, headless (multi-user.target)
- Wi-Fi (wlo1) is the only network interface in use
- Ethernet (eno1) present but unused
- Hostname: server
