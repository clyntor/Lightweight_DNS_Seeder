import pytest
import time
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

        # Wait a moment to ensure that the peers are updated
        time.sleep(1)

        # Print to verify that the peers are being updated
        print(f"IPv4 Peers: {resolver.ipv4_peers}")
        print(f"IPv6 Peers: {resolver.ipv6_peers}")

        # Ensure the mock was called exactly once
        assert mock_get.call_count == 1  # Ensure the API was called exactly once
        assert mock_get.return_value.json.return_value == mock_response  # Check if the response matches the mock

        # Test if peers are updated correctly
        assert len(resolver.ipv4_peers) == 1, f"Expected 1 IPv4 peer, got {len(resolver.ipv4_peers)}"
        assert len(resolver.ipv6_peers) == 1, f"Expected 1 IPv6 peer, got {len(resolver.ipv6_peers)}"
        assert resolver.ipv4_peers[0] == "192.168.1.1"
        assert resolver.ipv6_peers[0] == "2001:db8::ff00:42:8329"

# Test the resolve method (ensure it returns answers for A and AAAA queries)
def test_resolve():
    resolver = PeerResolver("https://api.adventurecoin.quest/peers")
    resolver.ipv4_peers = ["192.168.1.1"]
    resolver.ipv6_peers = ["2001:db8::ff00:42:8329"]

    # Mock request using dnslib's DNSRecord and QTYPE
    request_ipv4 = DNSRecord.question("example.com", "A")
    request_ipv6 = DNSRecord.question("example.com", "AAAA")

    # Mock response
    response_ipv4 = resolver.resolve(request_ipv4, None)
    response_ipv6 = resolver.resolve(request_ipv6, None)

    # Check for 'answers' in the response (using dnslib's rdata attribute)
    assert len(response_ipv4.rr) == 1
    # Extract rdata and compare with string using __str__()
    assert str(response_ipv4.rr[0].rdata) == "192.168.1.1"  # Compare rdata as string using __str__()

    assert len(response_ipv6.rr) == 1
    # Extract rdata and compare with string using __str__()
    assert str(response_ipv6.rr[0].rdata) == "2001:db8::ff00:42:8329"  # Compare rdata as string using __str__()
