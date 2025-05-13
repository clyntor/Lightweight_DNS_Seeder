import pytest
from unittest.mock import patch
from api_dns_seeder import PeerResolver
from dnslib import DNSRecord

# Test to ensure the resolver updates peers correctly
def test_update_peers():
    # Mock the API response
    mock_response = ["192.168.1.1", "2001:db8::ff00:42:8329"]

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Disable background thread for testing
        resolver = PeerResolver("https://api.adventurecoin.quest/peers", start_thread=False)

        # Directly call update_peers()
        resolver.update_peers()

        print(f"IPv4 Peers: {resolver.ipv4_peers}")
        print(f"IPv6 Peers: {resolver.ipv6_peers}")

        # Assert API was called once
        assert mock_get.call_count == 2
        assert mock_get.return_value.json.return_value == mock_response

        # Assert peers were parsed correctly
        assert len(resolver.ipv4_peers) == 1, f"Expected 1 IPv4 peer, got {len(resolver.ipv4_peers)}"
        assert len(resolver.ipv6_peers) == 1, f"Expected 1 IPv6 peer, got {len(resolver.ipv6_peers)}"
        assert resolver.ipv4_peers[0] == "192.168.1.1"
        assert resolver.ipv6_peers[0] == "2001:db8::ff00:42:8329"

# Test the resolve method (ensure it returns answers for A and AAAA queries)
def test_resolve():
    # Disable background thread for testing
    resolver = PeerResolver("https://api.adventurecoin.quest/peers", start_thread=False)
    resolver.ipv4_peers = ["192.168.1.1"]
    resolver.ipv6_peers = ["2001:db8::ff00:42:8329"]

    request_ipv4 = DNSRecord.question("example.com", "A")
    request_ipv6 = DNSRecord.question("example.com", "AAAA")

    response_ipv4 = resolver.resolve(request_ipv4, None)
    response_ipv6 = resolver.resolve(request_ipv6, None)

    assert len(response_ipv4.rr) == 1
    assert str(response_ipv4.rr[0].rdata) == "192.168.1.1"

    assert len(response_ipv6.rr) == 1
    assert str(response_ipv6.rr[0].rdata) == "2001:db8::ff00:42:8329"
