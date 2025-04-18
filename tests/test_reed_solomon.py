#
#  test_reed_solomon.py
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

import random

import pytest

from reed_solomon import ReedSolomon

@pytest.fixture
def reed_solomon():
    """Fixture to create an instance of the ReedSolomon class."""
    return ReedSolomon()

def test_encode(reed_solomon):
    """
    Test the encode method of the ReedSolomon class.
    """
    # Test data (up to 223 bytes)
    data = list()
    for i in range(random.randint(1, 223)):
        data.append(random.randint(0, 255))
    pad = 255 - 32 - len(data)

    # Encode the data
    parity = reed_solomon.encode(data, pad)

    # Check that the parity is 32 bytes long
    assert len(parity) == 32

    # Check that the parity is not all zeros (since the input data is non-zero)
    assert any(parity)  # At least one non-zero byte

def test_decode_no_errors(reed_solomon):
    """
    Test the decode method of the ReedSolomon class with no errors.
    """
    # Test data (up to 223 bytes)
    data = list()
    for i in range(random.randint(1, 223)):
        data.append(random.randint(0, 255))
    pad = 255 - 32 - len(data)

    # Encode the data to get the parity
    parity = reed_solomon.encode(data, pad)

    # Create the codeword (data + parity)
    codeword = data + parity

    # Decode the codeword
    decoded_data, error_positions, error_count = reed_solomon.decode(codeword, pad)

    # Check that the decoded data matches the original data
    assert decoded_data == data

    # Check that no errors were detected
    assert error_count == 0
    assert error_positions == []

@pytest.mark.parametrize('execution_number', range(10))
def test_decode_with_errors(reed_solomon, execution_number):
    """
    Test the decode method of the ReedSolomon class with correctable errors.
    """
    # Test data (up to 223 bytes)
    data = list()
    for i in range(random.randint(1, 223)):
        data.append(random.randint(0, 255))
    pad = 255 - 32 - len(data)

    # Encode the data to get the parity
    parity = reed_solomon.encode(data, pad)

    # Create the codeword (data + parity)
    codeword = data + parity

    # Introduce some errors in the codeword
    num_errors = random.randint(1, 16)
    err_pos = list()
    while len(err_pos) < num_errors:
        pos = random.randint(0, len(codeword) - 1)
        if not (pos in err_pos):
            err_pos.append(pos)

    for pos in err_pos:
        codeword[pos] = random.randint(0, 255)

    # Decode the codeword
    decoded_data, error_positions, error_count = reed_solomon.decode(codeword, pad)

    # Check that the decoded data matches the original data
    assert decoded_data == data

def test_decode_uncorrectable_errors(reed_solomon):
    """
    Test the decode method of the ReedSolomon class with uncorrectable errors.
    """
    # Test data (up to 223 bytes)
    data = list()
    for i in range(random.randint(1, 223)):
        data.append(random.randint(0, 255))
    pad = 255 - 32 - len(data)

    # Encode the data to get the parity
    parity = reed_solomon.encode(data, pad)

    # Create the codeword (data + parity)
    codeword = data + parity

    # Introduce too many errors (more than the code can correct)
    num_errors = random.randint(17, len(codeword))
    err_pos = list()
    for i in range(num_errors):
        err_pos.append(random.randint(0, len(codeword) - 1))

    for pos in err_pos:
        codeword[pos] = random.randint(0, 255)

    # Decode the codeword and expect an exception
    with pytest.raises(RuntimeError, match="Uncorrectable errors detected in Reed-Solomon codeword!"):
        reed_solomon.decode(codeword, pad)

def test_mod255(reed_solomon):
    """
    Test the _mod255 method of the ReedSolomon class.
    """
    # Test cases for _mod255
    for i in range(1000):
        num = random.randint(0, 2**16)
        assert reed_solomon._mod255(num) == num % 255
