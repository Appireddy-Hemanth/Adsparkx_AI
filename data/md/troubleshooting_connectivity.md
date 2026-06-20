# Troubleshooting Network Connectivity Issues

This document helps troubleshoot connectivity issues between your local network or application servers and the NovaSuite platform.

## 1. Diagnostic Steps
If you receive timeout errors or fail to connect to `api.novasuite.com`, follow these troubleshooting steps:
- **Ping Test**: Run `ping api.novasuite.com` in your terminal. Verify that DNS resolves to our active IP addresses.
- **Traceroute**: Run `traceroute api.novasuite.com` (macOS/Linux) or `tracert api.novasuite.com` (Windows) to identify where network packets are being dropped.
- **Port Check**: NovaSuite only accepts HTTPS traffic on port 443. Test connectivity to port 443 using telnet or nc:
  `nc -zv api.novasuite.com 443`

## 2. Firewall and Proxy Configuration
If your company uses a strict corporate firewall or proxy server, you may need to whitelist NovaSuite domains:
- Whitelist the following domains:
  - `*.novasuite.com`
  - `api.novasuite.com`
  - `cdn.novasuite.com`
- If your firewall requires static IP whitelisting, contact Enterprise Support at network-ops@novasuite.com to request our current IP address range. Note that we recommend whitelisting by domain name as IPs may change during maintenance.

## 3. SSL/TLS Certificate Issues
If you encounter SSL handshake failures or untrusted certificate warnings:
- Ensure your local operating system or programming environment has the latest root certificate authorities (CA) installed. NovaSuite certificates are signed by Let's Encrypt.
- Verify that your local clock is synchronized. Significant clock drift (more than 5 minutes) will cause SSL verification to fail.
- Do not bypass SSL validation in production scripts as this exposes your data to Man-in-the-Middle (MITM) attacks.