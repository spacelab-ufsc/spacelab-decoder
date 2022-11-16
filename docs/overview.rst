########
Overview 
########

The *Spacelab Decoder* is a Python in-development software to decode satellites telemetry from recorded audio file and subsequently real time decoding.

A list of known satellites that are planned to use this software so far are presented below:

* **FloripaSat-1** [1]_
* **GOLDS-UFSC (a.k.a. FloripaSat-2)** [2]_
* **Catarina-A1**

The satellites of the list above are developed (or in development) by the same research group: the *Space Technology Research Laboratory* (SpaceLab) [3]_, from *Universidade Federal de Santa Catarina* (Brazil).

The Software
============

.. image:: img/main-window.png
   :width: 700

The objective of this software is to become the "universal" software of the Spacelab's Satellites to decode the data from any of its satellites.

The main ways to achieve that are 

- to use a recorded audio file in the Wave format;
- and real time decoding using the an interface called Gqrx.

This application is written in Python, and is based on the experience gathered in the applications developed for the FloripaSat-1 mission. For telemetry encoding and transmission, there is also another application developed by the same research group, called *SpaceLab Transmitter* [4]_. The software also countains a logging system to register the events happening in the application.

More details of the software are described in the next sections of this documentation.

References
==========

.. [1] Marcelino, Gabriel M.; Martinez, Sara V.; Seman, Laio O., Slongo, Leonardo K.; Bezerra, Eduardo A. *A Critical Embedded System Challenge: The FloripaSat-1 Mission*. IEEE Latin America Transactions, Vol. 18, Issue 2, 2020.
.. [2] https://github.com/spacelab-ufsc/floripasat2-doc
.. [3] https://spacelab.ufsc.br/
.. [4] https://github.com/spacelab-ufsc/spacelab-transmitter