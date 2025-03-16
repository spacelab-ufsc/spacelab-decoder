#
#  test_golay24.py
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

from golay24 import Golay24

@pytest.fixture
def golay():
    return Golay24()

def test_encode_valid_data(golay):
    # Test encoding with valid 12-bit data
    data = 0xABC  # Example 12-bit data
    encoded = golay.encode(data)
    assert len(encoded) == 3  # Should return 3 bytes
    assert all(0 <= byte <= 255 for byte in encoded)  # Each byte should be valid

def test_encode_invalid_data(golay):
    # Test encoding with invalid data (outside 12-bit range)
    with pytest.raises(ValueError):
        golay.encode(0x1000)  # 13-bit data, should raise ValueError

def test_decode_valid_bytes(golay):
    # Test decoding with valid 24-bit Golay code
    encoded_bytes = [0x85, 0xE0, 0x90]  # Example encoded bytes
    decoded_data, errors_corrected = golay.decode(encoded_bytes)
    assert 0 <= decoded_data <= 0xFFF  # Should return valid 12-bit data
    assert isinstance(errors_corrected, int)  # Should return number of errors corrected

def test_decode_invalid_bytes(golay):
    # Test decoding with invalid input (wrong number of bytes or invalid byte values)
    with pytest.raises(ValueError):
        golay.decode([0xAB, 0xCD])  # Only 2 bytes, should raise ValueError

    with pytest.raises(ValueError):
        golay.decode([0xAB, 0xCD, 0x1000])  # Invalid byte value, should raise ValueError

def test_encode_decode_roundtrip(golay):
    # Test encoding followed by decoding should return the original data
    original_data = 0x123  # Example 12-bit data
    encoded = golay.encode(original_data)
    decoded_data, _ = golay.decode(encoded)
    assert decoded_data == original_data  # Should return the original data

def test_decode_with_errors(golay):
    # Test decoding with errors that can be corrected
    original_data = 0x123
    encoded = golay.encode(original_data)

    # Introduce a single-bit error
    encoded[0] ^= 0x01  # Flip one bit in the first byte
    decoded_data, errors_corrected = golay.decode(encoded)
    assert decoded_data == original_data  # Should correct the error and return original data
    assert errors_corrected == 1  # Should report 1 error corrected

def test_decode_uncorrectable_error(golay):
    # Test decoding with uncorrectable errors
    original_data = 0x123
    encoded = golay.encode(original_data)

    # Introduce multiple errors to make it uncorrectable
    encoded[0] ^= 0x01  # Flip one bit in the first byte
    encoded[1] ^= 0x01  # Flip one bit in the second byte
    encoded[2] ^= 0x01  # Flip one bit in the third byte
    decoded_data, errors_corrected = golay.decode(encoded)
    assert decoded_data == -1  # Should return -1 for uncorrectable errors
    assert errors_corrected is None  # Should return None for uncorrectable errors

def test_B(golay):
    # Test cases for the _B method
    # Case 1: i = 0 (first row of the identity matrix)
    assert golay._B(0) == 0b100000000000  # 1 << 11

    # Case 2: i = 1 (second row of the identity matrix)
    assert golay._B(1) == 0b010000000000  # 1 << 10

    # Case 3: i = 5 (middle row of the identity matrix)
    assert golay._B(5) == 0b000001000000  # 1 << 6

    # Case 4: i = 11 (last row of the identity matrix)
    assert golay._B(11) == 0b000000000001  # 1 << 0

    # Case 5: i = 6 (another middle row of the identity matrix)
    assert golay._B(6) == 0b000000100000  # 1 << 5

    # Case 6: i = 3 (another row of the identity matrix)
    assert golay._B(3) == 0b000100000000  # 1 << 8

    # Case 7: i = 10 (second-to-last row of the identity matrix)
    assert golay._B(10) == 0b000000000010  # 1 << 1

    # Case 8: i = 7 (another middle row of the identity matrix)
    assert golay._B(7) == 0b000000010000  # 1 << 4

    # Case 9: i = 4 (another row of the identity matrix)
    assert golay._B(4) == 0b000010000000  # 1 << 7

    # Case 10: i = 2 (another row of the identity matrix)
    assert golay._B(2) == 0b001000000000  # 1 << 9

    # Case 11: i = 8 (another middle row of the identity matrix)
    assert golay._B(8) == 0b000000001000  # 1 << 3

    # Case 12: i = 9 (another row of the identity matrix)
    assert golay._B(9) == 0b000000000100  # 1 << 2

def test_hamming_weight(golay):
    # Test cases for the _hamming_weight method
    # Case 1: All bits are 0
    assert golay._hamming_weight(0b0000) == 0

    # Case 2: All bits are 1
    assert golay._hamming_weight(0b1111) == 4

    # Case 3: Mixed bits
    assert golay._hamming_weight(0b1010) == 2
    assert golay._hamming_weight(0b1101) == 3

    # Case 4: Single bit set
    assert golay._hamming_weight(0b0001) == 1
    assert golay._hamming_weight(0b1000) == 1

    # Case 5: Large number with multiple bits set
    assert golay._hamming_weight(0b1111111111111111) == 16

    # Case 6: Edge case with maximum 32-bit integer
    assert golay._hamming_weight(0xFFFFFFFF) == 32

    # Case 7: Edge case with minimum value (0)
    assert golay._hamming_weight(0) == 0

    # Case 8: Random number
    assert golay._hamming_weight(0b101010101010) == 6

    # Case 9: Number with alternating bits
    assert golay._hamming_weight(0b01010101) == 4
