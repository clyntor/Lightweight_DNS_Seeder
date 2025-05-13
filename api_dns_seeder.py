import requests
import time
import threading
from dnslib.server import DNSServer, DNSHandler, BaseResolver
from dnslib.dns import RR, QTYPE, A
from ipaddress import ip_address

class PeerResolver(BaseResolver):
    def __init__(self, api_url):
        self.api_url = api_url
        self.peer_ips = []
        self.lock = threading.Lock()
        self.update_peers()

        # Background update loop
        threading.Thread(target=self.update_loop, daemon=True).start()

    def update_peers(self):
        try:
            response = requests.get(self.api_url)
            if response.status_code == 200:
                peers = response.json()
                with self.lock:
                    self.peer_ips = [
                        ip for ip in peers
                        if self.is_valid_ipv4(ip)
                    ]
        except Exception as e:
            print(f"Failed to fetch peers: {e}")

    def update_loop(self):
        while True:
            self.update_peers()
            time.sleep(300)  # Refresh every 5 mins

    def resolve(self, request, handler):
        reply = request.reply()
        qname = request.q.qname
        qtype = QTYPE[request.q.qtype]
        with self.lock:
            for ip in self.peer_ips:
                reply.add_answer(RR(qname, QTYPE.A, rdata=A(ip), ttl=60))
        return reply

    @staticmethod
    def is_valid_ipv4(ip):
        try:
            return ip_address(ip).version == 4
        except:
            return False

# Start DNS server
if __name__ == "__main__":
    resolver = PeerResolver("https://api.adventurecoin.quest/peers")
    server = DNSServer(resolver, port=53, address="0.0.0.0")
    print("Starting DNS Seeder on port 53...")
    server.start()
