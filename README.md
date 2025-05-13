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
