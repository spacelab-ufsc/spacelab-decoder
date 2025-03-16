#
#  test_byte_buffer.py
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

from byte_buffer import ByteBuffer, _BYTE_BUFFER_MSB, _BYTE_BUFFER_LSB

@pytest.fixture
def byte_buffer_msb():
    # Create a ByteBuffer object with MSB endianness
    return ByteBuffer(_BYTE_BUFFER_MSB)

@pytest.fixture
def byte_buffer_lsb():
    # Create a ByteBuffer object with LSB endianness
    return ByteBuffer(_BYTE_BUFFER_LSB)

def test_init_default_endianness():
    # Test initialization with default endianness (MSB)
    buffer = ByteBuffer()
    assert buffer.endianess == _BYTE_BUFFER_MSB
    assert buffer.pos == 7
    assert buffer.buffer == [False] * 8

def test_init_custom_endianness():
    # Test initialization with custom endianness (LSB)
    buffer = ByteBuffer(_BYTE_BUFFER_LSB)
    assert buffer.endianess == _BYTE_BUFFER_LSB
    assert buffer.pos == 7
    assert buffer.buffer == [False] * 8

def test_is_full(byte_buffer_msb):
    # Test is_full method
    assert not byte_buffer_msb.is_full()  # Buffer should not be full initially

    # Fill the buffer
    for _ in range(8):
        byte_buffer_msb.push(True)

    assert byte_buffer_msb.is_full()  # Buffer should be full after pushing 8 bits

def test_push_valid_bit(byte_buffer_msb):
    # Test pushing valid bits (boolean values)
    byte_buffer_msb.push(True)
    byte_buffer_msb.push(False)
    assert byte_buffer_msb.buffer[7] == True
    assert byte_buffer_msb.buffer[6] == False
    assert byte_buffer_msb.pos == 5  # Position should decrement after each push

def test_push_invalid_bit(byte_buffer_msb):
    # Test pushing invalid bits (non-boolean values)
    with pytest.raises(RuntimeError):
        byte_buffer_msb.push(1)  # Should raise RuntimeError for non-boolean input

def test_clear(byte_buffer_msb):
    # Test clear method
    byte_buffer_msb.push(True)
    byte_buffer_msb.push(False)
    byte_buffer_msb.clear()
    assert byte_buffer_msb.buffer == [False] * 8  # Buffer should be reset
    assert byte_buffer_msb.pos == 7  # Position should be reset to 7

def test_to_byte_msb(byte_buffer_msb):
    # Test to_byte method with MSB endianness
    byte_buffer_msb.push(True)
    byte_buffer_msb.push(False)
    byte_buffer_msb.push(True)
    byte_buffer_msb.push(False)
    assert byte_buffer_msb.to_byte() == 0b00000101

def test_to_byte_lsb(byte_buffer_lsb):
    # Test to_byte method with LSB endianness
    byte_buffer_lsb.push(True)
    byte_buffer_lsb.push(False)
    byte_buffer_lsb.push(True)
    byte_buffer_lsb.push(False)
    assert byte_buffer_lsb.to_byte() == 0b10100000

def test_repr(byte_buffer_msb):
    # Test __repr__ method
    byte_buffer_msb.push(True)
    byte_buffer_msb.push(False)
    assert repr(byte_buffer_msb) == str([False, False, False, False, False, False, False, True])

def test_str(byte_buffer_msb):
    # Test __str__ method
    byte_buffer_msb.push(True)
    byte_buffer_msb.push(False)
    assert str(byte_buffer_msb) == str([False, False, False, False, False, False, False, True])
