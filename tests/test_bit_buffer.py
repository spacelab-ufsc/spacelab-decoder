#
#  test_bit_buffer.py
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

from bit_buffer import BitBuffer, _BIT_BUFFER_MSB, _BIT_BUFFER_LSB

@pytest.fixture
def bit_buffer_msb():
    # Create a BitBuffer object with MSB endianness
    return BitBuffer(endi=_BIT_BUFFER_MSB)

@pytest.fixture
def bit_buffer_lsb():
    # Create a BitBuffer object with LSB endianness
    return BitBuffer(endi=_BIT_BUFFER_LSB)

def test_init_default_size_and_endianness():
    # Test initialization with default size (8) and endianness (MSB)
    buffer = BitBuffer()
    assert buffer.get_max_size() == 8
    assert buffer.endianess == _BIT_BUFFER_MSB
    assert len(buffer) == 0  # Buffer should be empty initially

def test_init_custom_size_and_endianness():
    # Test initialization with custom size and endianness
    buffer = BitBuffer(size=16, endi=_BIT_BUFFER_LSB)
    assert buffer.get_max_size() == 16
    assert buffer.endianess == _BIT_BUFFER_LSB
    assert len(buffer) == 0  # Buffer should be empty initially

def test_set_max_size_valid():
    # Test setting a valid maximum size
    buffer = BitBuffer()
    buffer.set_max_size(16)
    assert buffer.get_max_size() == 16

def test_set_max_size_invalid():
    # Test setting an invalid maximum size (non-integer)
    buffer = BitBuffer()
    with pytest.raises(RuntimeError):
        buffer.set_max_size("invalid")  # Should raise RuntimeError

def test_set_endianess_valid():
    # Test setting valid endianness (MSB and LSB)
    buffer = BitBuffer()
    buffer.set_endianess(_BIT_BUFFER_MSB)
    assert buffer.endianess == _BIT_BUFFER_MSB

    buffer.set_endianess(_BIT_BUFFER_LSB)
    assert buffer.endianess == _BIT_BUFFER_LSB

def test_set_endianess_invalid():
    # Test setting invalid endianness
    buffer = BitBuffer()
    with pytest.raises(RuntimeError):
        buffer.set_endianess("invalid")  # Should raise RuntimeError

def test_push_msb(bit_buffer_msb):
    # Test pushing bits with MSB endianness
    bit_buffer_msb.push(True)
    bit_buffer_msb.push(False)
    bit_buffer_msb.push(True)
    assert bit_buffer_msb == [True, False, True]  # Bits should be appended in MSB order

def test_push_lsb(bit_buffer_lsb):
    # Test pushing bits with LSB endianness
    bit_buffer_lsb.push(True)
    bit_buffer_lsb.push(False)
    bit_buffer_lsb.push(True)
    assert bit_buffer_lsb == [True, False, True]  # Bits should be inserted at the beginning in LSB order

def test_push_max_size_msb(bit_buffer_msb):
    # Test pushing bits beyond the maximum size with MSB endianness
    for _ in range(10):  # Push 10 bits (max size is 8)
        bit_buffer_msb.push(True)
    assert len(bit_buffer_msb) == 8  # Buffer should not exceed max size
    assert bit_buffer_msb == [True] * 8  # Oldest bits should be discarded

def test_push_max_size_lsb(bit_buffer_lsb):
    # Test pushing bits beyond the maximum size with LSB endianness
    for _ in range(10):  # Push 10 bits (max size is 8)
        bit_buffer_lsb.push(True)
    assert len(bit_buffer_lsb) == 8  # Buffer should not exceed max size
    assert bit_buffer_lsb == [True] * 8  # Oldest bits should be discarded

def test_push_invalid_bit(bit_buffer_msb):
    # Test pushing invalid bits (non-boolean and non-integer)
    with pytest.raises(RuntimeError):
        bit_buffer_msb.push("invalid")  # Should raise RuntimeError

def test_to_int_msb(bit_buffer_msb):
    # Test converting buffer to integer with MSB endianness
    bit_buffer_msb.push(True)
    bit_buffer_msb.push(False)
    bit_buffer_msb.push(True)
    assert bit_buffer_msb.to_int() == 0b101  # MSB: 101

def test_to_int_lsb(bit_buffer_lsb):
    # Test converting buffer to integer with LSB endianness
    bit_buffer_lsb.push(True)
    bit_buffer_lsb.push(False)
    bit_buffer_lsb.push(True)
    assert bit_buffer_lsb.to_int() == 0b101  # LSB: 101
