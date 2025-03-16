#
#  test_sync_word.py
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

from sync_word import SyncWord, _SYNC_WORD_MSB, _SYNC_WORD_LSB

@pytest.fixture
def sync_word_msb():
    # Create a SyncWord object with MSB endianness
    return SyncWord([0xAB, 0xCD], _SYNC_WORD_MSB)

@pytest.fixture
def sync_word_lsb():
    # Create a SyncWord object with LSB endianness
    return SyncWord([0xAB, 0xCD], _SYNC_WORD_LSB)

def test_init_valid_input():
    # Test initialization with valid input (list of bytes)
    sync_word = SyncWord([0xAB, 0xCD], _SYNC_WORD_MSB)
    assert isinstance(sync_word, SyncWord)
    assert len(sync_word) == 16  # 2 bytes * 8 bits = 16 bits

def test_init_invalid_input():
    # Test initialization with invalid input (non-list)
    with pytest.raises(RuntimeError):
        SyncWord(0xAB, _SYNC_WORD_MSB)  # Should raise RuntimeError

def test_str_representation_msb(sync_word_msb):
    # Test string representation for MSB endianness
    expected_str = "[171, 205] = [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1]"
    assert str(sync_word_msb) == expected_str

def test_str_representation_lsb(sync_word_lsb):
    # Test string representation for LSB endianness
    expected_str = "[213, 179] = [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1]"
    assert str(sync_word_lsb) == expected_str

def test_eq_identical_msb(sync_word_msb):
    # Test equality with an identical SyncWord (MSB)
    other = SyncWord([0xAB, 0xCD], _SYNC_WORD_MSB)
    assert sync_word_msb == other  # All bits should match
    assert len(sync_word_msb) == len(other)  # Lengths should match

def test_eq_identical_lsb(sync_word_lsb):
    # Test equality with an identical SyncWord (LSB)
    other = SyncWord([0xAB, 0xCD], _SYNC_WORD_LSB)
    assert sync_word_lsb == other  # All bits should match
    assert len(sync_word_lsb) == len(other)  # Lengths should match

def test_eq_different_patterns(sync_word_msb):
    # Test equality with a SyncWord that has a different bit pattern
    other = SyncWord([0x12, 0x34], _SYNC_WORD_MSB)
    assert sync_word_msb != other  # Bits should not match
    assert len(sync_word_msb) == len(other)  # Lengths should match

def test_eq_non_list_object(sync_word_msb):
    # Test equality with a non-list object
    other = "not a list"
    assert type(sync_word_msb == other) is not int  # Should return NotImplemented for non-list objects

def test_eq_shorter_list(sync_word_msb):
    # Test equality with a list that is shorter than the SyncWord
    other = [True, False, True]  # Shorter list
    assert (sync_word_msb == other) == 0    # Should return 0 for shorter lists

def test_eq_partial_match(sync_word_msb):
    # Test equality with a list that partially matches the SyncWord
    other = SyncWord([0xAB, 0x00], _SYNC_WORD_MSB)  # Partially matches
    equal_bits = sync_word_msb == other
    assert equal_bits > 0  # Some bits should match
    assert equal_bits < len(sync_word_msb)  # Not all bits should match

def test_eq_empty_list(sync_word_msb):
    # Test equality with an empty list
    other = []
    assert (sync_word_msb == other) == 0    # Should return 0 for empty lists

def test_byte_to_bitfield_msb():
    # Test byte_to_bitfield with MSB endianness
    sync_word = SyncWord([0xAB], _SYNC_WORD_MSB)
    expected_bitfield = [True, False, True, False, True, False, True, True]  # 0xAB in MSB
    assert sync_word.byte_to_bitfield(0xAB) == expected_bitfield

def test_byte_to_bitfield_lsb():
    # Test byte_to_bitfield with LSB endianness
    sync_word = SyncWord([0xAB], _SYNC_WORD_LSB)
    expected_bitfield = [True, True, False, True, False, True, False, True]  # 0xAB in LSB
    assert sync_word.byte_to_bitfield(0xAB) == expected_bitfield
