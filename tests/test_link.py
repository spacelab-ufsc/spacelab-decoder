#
#  test_slp.py
#  
#  Copyright The SpaceLab-Decoder Contributors.
#  
#  This file is part of SpaceLab-Decoder.
#
#  SpaceLab-Decoder is free software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  SpaceLab-Decoder is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public
#  License along with SpaceLab-Decoder; if not, see <http://www.gnu.org/licenses/>.
#  
#

import pytest

from link import Link

@pytest.fixture
def sample_link():
    """Fixture to create a Link instance with sample data."""
    link = Link()
    link.set_id("1")
    link.set_name("TestLink")
    link.set_direction("up")
    link.set_frequency(435000000)
    link.set_modulation("GFSK")
    link.set_baudrate(9600)
    link.set_preamble([0xAA, 0xAA])
    link.set_sync_word([0x55, 0x55])
    link.set_link_protocol("AX.25")
    link.set_network_protocol("IP")
    return link

def test_set_get_id(sample_link):
    """Test setting and getting the link ID."""
    link = sample_link
    assert link.get_id() == "1"

def test_set_get_name(sample_link):
    """Test setting and getting the link name."""
    link = sample_link
    assert link.get_name() == "TestLink"

def test_set_get_direction(sample_link):
    """Test setting and getting the link direction."""
    link = sample_link
    assert link.get_direction() == "up"

    # Test invalid direction
    with pytest.raises(ValueError):
        link.set_direction("invalid")

def test_set_get_frequency(sample_link):
    """Test setting and getting the link frequency."""
    link = sample_link
    assert link.get_frequency() == 435000000

def test_set_get_modulation(sample_link):
    """Test setting and getting the link modulation."""
    link = sample_link
    assert link.get_modulation() == "GFSK"

def test_set_get_baudrate(sample_link):
    """Test setting and getting the link baudrate."""
    link = sample_link
    assert link.get_baudrate() == 9600

def test_set_get_preamble(sample_link):
    """Test setting and getting the link preamble."""
    link = sample_link
    assert link.get_preamble() == [0xAA, 0xAA]

def test_set_get_sync_word(sample_link):
    """Test setting and getting the link sync word."""
    link = sample_link
    assert link.get_sync_word() == [0x55, 0x55]

def test_set_get_link_protocol(sample_link):
    """Test setting and getting the link protocol."""
    link = sample_link
    assert link.get_link_protocol() == "AX.25"

def test_set_get_network_protocol(sample_link):
    """Test setting and getting the network protocol."""
    link = sample_link
    assert link.get_network_protocol() == "IP"

def test_str_method(sample_link):
    """Test the string representation of the Link class."""
    link = sample_link
    expected_output = (
        "Name: TestLink\n\r"
        "Direction: up\n\r"
        "Frequency: 435000000\n\r"
        "Modulation: GFSK\n\r"
        "Baudrate: 9600\n\r"
        "Preamble: [170, 170]\n\r"
        "Sync. Word: [85, 85]\n\r"
        "Link protocol: AX.25\n\r"
        "Network protocol: IP\n\r"
    )
    assert str(link) == expected_output
