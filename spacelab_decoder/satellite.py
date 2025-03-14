#
#  satellite.py
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

import json

from spacelab_decoder.link import Link

class Satellite:
    """
    Satellite object.
    """
    def __init__(self):
        """
        Class constructor.
        """
        self._name = ""
        self._links = list()
        self._link = None

    def __str__(self):
        """
        String representation of the satellite.

        :return: A text description of the satellite.
        :rtype: str
        """
        txt = "Satellite: " + self.get_name() + "\n\r"
        txt += "Links:" + "\n\r"
        links = self.get_links()
        for l in links:
            txt += str(l)

        return txt

    def load_from_file(self, filename):
        """
        Loads the satellite parameters from a JSON file.

        :param filename: Is the name of the file to load.
        :type: str

        :return: None
        """
        with open(filename) as f:
            sat_info = json.load(f)

            if 'name' in sat_info:
                self.set_name(sat_info['name'])
            else:
                raise RuntimeError("The satellite configuration file is corrupted!")

            if 'links' in sat_info:
                links = list()
                for i in range(len(sat_info['links'])):
                    link = Link()

                    link.set_id(sat_info['links'][i]['id'])
                    link.set_name(sat_info['links'][i]['name'])
                    link.set_direction(sat_info['links'][i]['direction'])
                    link.set_frequency(int(sat_info['links'][i]['frequency']))
                    link.set_modulation(sat_info['links'][i]['modulation'])
                    link.set_baudrate(sat_info['links'][i]['baudrate'])
                    link.set_preamble(sat_info['links'][i]['preamble'])
                    link.set_sync_word(sat_info['links'][i]['sync_word'])
                    link.set_link_protocol(sat_info['links'][i]['protocol_link'])
                    link.set_network_protocol(sat_info['links'][i]['protocol_network'])

                    links.append(link)

                self.set_links(links)
            else:
                raise RuntimeError("The satellite configuration file is corrupted!")

    def set_name(self, name):
        """
        Sets the name of the satellite.

        :param name: Is the name of the satellite.
        :type: string

        :return None.
        """
        self._name = name

    def get_name(self):
        """
        Gets the name of the satellite.

        :return: The name of the satellite.
        :rtype: string
        """
        return self._name

    def set_links(self, links):
        """
        Sets the list of communication links.

        :param links: Is a list with communication links
        :type: list

        :return: None
        """
        self._links = links.copy()

    def get_links(self):
        """
        Gets the communication links.

        :return: A list with all available communication links.
        :rtype: list
        """
        return self._links

    def set_active_link(self, idx):
        """
        Sets the current active communication link.

        :param idx: Is the index of the current active link.
        :type: int

        :return: None.
        """
        self._link = self.get_links()[idx]

    def get_active_link(self):
        """
        Gets the active communication link.

        :return: The current active link.
        :rtype: Link
        """
        return self._link
