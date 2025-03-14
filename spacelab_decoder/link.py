#
#  link.py
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

class Link:
    """
    Communication link object.
    """
    def __init__(self):
        """
        Class constructor.
        """
        self._id                = str()
        self._name              = str()
        self._direction         = str()
        self._frequency         = int()
        self._modulation        = str()
        self._baudrate          = int()
        self._preamble          = list()
        self._sync_word         = list()
        self._protocol_link     = str()
        self._protocol_network  = str()

    def __str__(self):
        """
        String representation of the communication link.

        :return: A text description of the link configuration.
        :rtype: str
        """
        txt =  "Name: " + self.get_name() + "\n\r"
        txt += "Direction: " + self.get_direction() + "\n\r"
        txt += "Frequency: " + str(self.get_frequency()) + "\n\r"
        txt += "Modulation: " + self.get_modulation() + "\n\r"
        txt += "Baudrate: " + str(self.get_baudrate()) + "\n\r"
        txt += "Preamble: " + str(self.get_preamble()) + "\n\r"
        txt += "Sync. Word: " + str(self.get_sync_word()) + "\n\r"
        txt += "Link protocol: " + self.get_link_protocol() + "\n\r"
        txt += "Network protocol: " + self.get_network_protocol() + "\n\r"

        return txt

    def set_id(self, id):
        """
        Sets the ID of the communication link.

        :param id: Is the ID of the communication link as an string.
        :type: str

        :return: None.
        """
        self._id = id

    def get_id(self):
        """
        Gets the ID of the communication link.

        :return: The ID of the link.
        :rtype: str
        """
        return self._id

    def set_name(self, name):
        """
        Sets the name of the communication link.

        :param name: Is the name of the link.
        :type: str

        :return: None
        """
        self._name = name

    def get_name(self):
        """
        Gets the link name.

        :return: The name of the link.
        :rtype: str
        """
        return self._name

    def set_direction(self, dir):
        """
        Sets the direction of the communication link ("up" or "down").

        :param dir: Is the direction of the communication link.
        :type: str

        :return: None
        """
        dir = dir.lower()
        if dir == "up" or dir == "down":
            self._direction = dir
        else:
            raise ValueError('The direction of the communication link must be \"up\" or \"down\"!')

    def get_direction(self):
        """
        Gets the direction of the communication link.

        :return: The direction of the communication link.
        :rtype: str
        """
        return self._direction

    def set_frequency(self, freq):
        """
        Sets the frequency of the communication link.

        :param freq: Is the frequency in Hertz.
        :type: int

        :return: None
        """
        self._frequency = freq

    def get_frequency(self):
        """
        Gets the frequency of the communication link.

        :return: The frequency of the communication link in Hertz.
        :rtype: int
        """
        return self._frequency

    def set_modulation(self, mod):
        """
        Sets the modulation of the communication link.

        :param mod: Is the name of the modulation of the communication link.
        :type: str

        :return: None.
        """
        self._modulation = mod

    def get_modulation(self):
        """
        Gets the modulation of the communication link.

        :return: The name of the modulation.
        :rtype: str
        """
        return self._modulation

    def set_baudrate(self, baud):
        """
        Sets the baudrate of the communication link.

        :param baud: Is the new baudrate in bps.
        :type: int

        :return: None
        """
        self._baudrate = baud

    def get_baudrate(self):
        """
        Gets the baurdate of the communication link.

        :return: The baudrate of the link in bps.
        :rtype: int
        """
        return self._baudrate

    def set_preamble(self, preamb):
        """
        Sets the preamble of the communication link.

        :param preamb: Is the list with the preamble sequence as integers.
        :type: list

        :return: None
        """
        self._preamble = preamb

    def get_preamble(self):
        """
        Gets the preamble sequence of the communication link.

        :return: The preamble sequence as a list of integers
        :rtype: list
        """
        return self._preamble

    def set_sync_word(self, sw):
        """
        Sets the sync word of the communication link.

        :param sw: Is the sync word as a list of integers.
        :type: list

        :return: None
        """
        self._sync_word = sw.copy()

    def get_sync_word(self):
        """
        Gets the sync word of the communication link.

        :return: The sync word as a list of integers.
        :rtype: list
        """
        return self._sync_word

    def set_link_protocol(self, prot):
        """
        Sets the protocol of the data link layer of the communication link.

        :param prot: Is the name of the data link layer protocol.
        :type: str

        :return: None
        """
        self._protocol_link = prot

    def get_link_protocol(self):
        """
        Gets the protocol of the data link layer of the communication link.

        :return: The name of the data link layer protocol.
        :rtype: str
        """
        return self._protocol_link

    def set_network_protocol(self, prot):
        """
        Sets the protocol of the network layer of the communication link.

        :param prot: Is the name of the network layer protocol.
        :type: str

        :return: None
        """
        self._protocol_network = prot

    def get_network_protocol(self):
        """
        Gets the protocol of the network layer of the communication link.

        :return: The name of the network layer protocol.
        :rtype: str
        """
        return self._protocol_network
