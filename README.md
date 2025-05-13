# Lightweight_DNS_Seeder
API-Driven Lightweight DNS Seeder

# Install dnslib:
```bash
pip install dnslib requests
```

# 🌐 Final Steps
1. Point your DNS (e.g., seed.adventurecoin.quest) to the server running this.

2. Open port 53 (UDP + TCP) in your firewall and hosting provider.

3. In your coin’s chainparams.cpp, make sure you have:

```cpp
vSeeds.emplace_back("seed.adventurecoin.quest");
```


# 🧠 Just make sure you also:
Run the script with root privileges or use sudo, since binding to port 53 (standard DNS port) requires elevated permissions.

Example:

```bash
sudo python3 api_dns_seeder.py
```
Open port 53 (both UDP and TCP) in your firewall:

```bash
sudo ufw allow 53
```
Point your DNS A record to the server's IP (e.g., seed.adventurecoin.quest → your.server.ip).
