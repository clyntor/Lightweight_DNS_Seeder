import pytest
import time  # Import the time module
from unittest.mock import patch
from api_dns_seeder import PeerResolver
from dnslib import DNSRecord, QTYPE


# Test to ensure the resolver updates peers correctly
def test_update_peers():
    # Mock the API response
    mock_response = {
        "peers": ["192.168.1.1", "2001:db8::ff00:42:8329"]
    }

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response
        resolver = PeerResolver("https://api.adventurecoin.quest/peers")
        
        # Directly call update_peers() instead of waiting for the thread
        resolver.update_peers()

        # Test if peers are updated
        assert len(resolver.ipv4_peers) == 1
        assert len(resolver.ipv6_peers) == 1
        assert resolver.ipv4_peers[0] == "192.168.1.1"
        assert resolver.ipv6_peers[0] == "2001:db8::ff00:42:8329"


# Test the resolve method (ensure it returns answers for A and AAAA queries)
def test_resolve():
    resolver = PeerResolver("https://api.adventurecoin.quest/peers")
    resolver.ipv4_peers = ["192.168.1.1"]
    resolver.ipv6_peers = ["2001:db8::ff00:42:8329"]

    # Mock request using dnslib's DNSRecord and QTYPE
    request_ipv4 = DNSRecord.question("example.com", "A")  # Use string "A" instead of QTYPE.A
    request_ipv6 = DNSRecord.question("example.com", "AAAA")  # Use string "AAAA" instead of QTYPE.AAAA

    # Mock response
    response_ipv4 = resolver.resolve(request_ipv4, None)
    response_ipv6 = resolver.resolve(request_ipv6, None)

    # Test IPv4 resolution
    assert len(response_ipv4.answers) == 1
    assert response_ipv4.answers[0].rdata == "192.168.1.1"

    # Test IPv6 resolution
    assert len(response_ipv6.answers) == 1
    assert response_ipv6.answers[0].rdata == "2001:db8::ff00:42:8329"
