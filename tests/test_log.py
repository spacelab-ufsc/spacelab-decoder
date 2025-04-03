#
#  test_log.py
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

import os
import csv
from datetime import datetime
from log import Log

import pytest

@pytest.fixture
def temp_log(tmp_path):
    """Fixture that creates a temporary log file for testing."""
    filename = "test_log.csv"
    path = tmp_path
    return Log(filename, str(path))

def test_initialization(temp_log):
    """Test the initialization of the Log class."""
    assert temp_log.get_filename() == "test_log.csv"
    assert temp_log.get_path() is not None

def test_set_filename(temp_log):
    """Test the set_filename method."""
    temp_log.set_filename("new_log.csv")
    assert temp_log.get_filename() == "new_log.csv"

def test_set_path(temp_log, tmp_path):
    """Test the set_path method."""
    new_path = tmp_path / "subdir"
    temp_log.set_path(str(new_path))
    assert temp_log.get_path() == str(new_path)

def test_write_without_timestamp(temp_log, tmp_path):
    """Test writing a log message without a timestamp."""
    test_msg = "Test message without timestamp"
    temp_log.write(test_msg)

    log_file = tmp_path / temp_log.get_filename()
    assert log_file.exists()

    with open(log_file, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)

    assert len(rows) == 1
    assert rows[0][1] == test_msg
    # Verify the timestamp is roughly correct (within 1 second)
    logged_time = datetime.strptime(rows[0][0], "%Y-%m-%d %H:%M:%S.%f")
    assert (datetime.now() - logged_time).total_seconds() < 1

def test_write_with_timestamp(temp_log, tmp_path):
    """Test writing a log message with a specific timestamp."""
    test_msg = "Test message with timestamp"
    test_ts = "2023-01-01 12:00:00.000000"
    temp_log.write(test_msg, test_ts)

    log_file = tmp_path / temp_log.get_filename()
    assert log_file.exists()

    with open(log_file, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)

    assert len(rows) == 1
    assert rows[0][0] == test_ts
    assert rows[0][1] == test_msg

def test_multiple_writes(temp_log, tmp_path):
    """Test writing multiple log messages."""
    messages = ["First message", "Second message", "Third message"]
    for msg in messages:
        temp_log.write(msg)

    log_file = tmp_path / temp_log.get_filename()
    assert log_file.exists()

    with open(log_file, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)

    assert len(rows) == len(messages)
    for i, row in enumerate(rows):
        assert row[1] == messages[i]

def test_write_to_nonexistent_directory(tmp_path):
    """Test that the class creates the directory if it doesn't exist."""
    new_dir = tmp_path / "new_directory"
    log = Log("test_log.csv", str(new_dir))

    # Directory shouldn't exist yet
    assert not new_dir.exists()

    # Write should create the directory
    log.write("Test message")
    assert new_dir.exists()

def test_write_empty_message(temp_log, tmp_path):
    """Test writing an empty message."""
    temp_log.write("")

    log_file = tmp_path / temp_log.get_filename()
    with open(log_file, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)

    assert len(rows) == 1
    assert rows[0][1] == ""

def test_write_special_characters(temp_log, tmp_path):
    """Test writing messages with special characters."""
    test_msg = "Test message with \t tabs \n and newlines"
    temp_log.write(test_msg)

    log_file = tmp_path / temp_log.get_filename()
    with open(log_file, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)

    assert len(rows) == 1
    # The tab in the message shouldn't affect the parsing since we're using tab as delimiter
    assert rows[0][1] == test_msg
