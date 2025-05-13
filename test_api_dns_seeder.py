import pytest
import time  # Import the time module
from unittest.mock import patch
from api_dns_seeder import PeerResolver


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
        
        # Give the background thread time to update peers
        time.sleep(1)
        
        assert len(resolver.ipv4_peers) == 1
        assert len(resolver.ipv6_peers) == 1
        assert resolver.ipv4_peers[0] == "192.168.1.1"
        assert resolver.ipv6_peers[0] == "2001:db8::ff00:42:8329"


# Test the resolve method (ensure it returns answers for A and AAAA queries)
def test_resolve():
    resolver = PeerResolver("https://api.adventurecoin.quest/peers")
    resolver.ipv4_peers = ["192.168.1.1"]
    resolver.ipv6_peers = ["2001:db8::ff00:42:8329"]

    # Mock request
    class MockRequest:
        def __init__(self, qtype, qname):
            self.q = type('q', (object,), {'qtype': qtype, 'qname': qname})
    
    # Test IPv4 resolution
    request_ipv4 = MockRequest('A', 'example.com')
    response_ipv4 = resolver.resolve(request_ipv4, None)
    assert len(response_ipv4.answers) == 1
    assert response_ipv4.answers[0].rdata == "192.168.1.1"

    # Test IPv6 resolution
    request_ipv6 = MockRequest('AAAA', 'example.com')
    response_ipv6 = resolver.resolve(request_ipv6, None)
    assert len(response_ipv6.answers) == 1
    assert response_ipv6.answers[0].rdata == "2001:db8::ff00:42:8329"
