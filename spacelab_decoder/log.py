#
#  log.py
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

from datetime import datetime
import os
import csv

class Log:
    """
    Log handling class.
    """
    def __init__(self, filename, path):
        """
        Constructor.

        :param filename: Is the name of the log file.
        :type: str

        :param path: Is the path to save the log file.
        :type: str

        :return: None
        """
        self.set_filename(filename)
        self.set_path(path)

    def set_filename(self, filename):
        """
        Sets the name of the log file.

        :param filename: Is the name of the log file.
        :type: str

        :return: None
        """
        self._filename = filename

    def get_filename(self):
        """
        Gets the name of the log file.

        :return: The name of the log file.
        :rtype: str
        """
        return self._filename

    def set_path(self, path):
        """
        Sets the path of the log file.

        :param path: Is the path to save the log file.
        :type: str

        :return: None
        """
        self._path = path

    def get_path(self):
        """
        Gets the path of the log file.

        :return: The path of the log file.
        :rtype: str
        """
        return self._path

    def write(self, msg, ts=None):
        """
        Writes a log message to the log file.

        :param msg: Is the log message to write.
        :type: str

        :param ts: Is the timestamp of the log event as an string.
        :type: str

        :return: None.
        """
        event = list()
        if ts is None:
            event = [str(datetime.now()), msg]
        else:
            event = [ts, msg]

        if not os.path.exists(self.get_path()):
            os.mkdir(self.get_path())

        with open(self.get_path() + '/' + self.get_filename(), 'a') as logfile:
            writer = csv.writer(logfile, delimiter='\t')
            writer.writerow(event)
