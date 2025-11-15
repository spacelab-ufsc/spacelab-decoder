*****
Usage
*****

How It Works
------------

The SpaceLab Decoder works by processing audio signals or UDP data streams to extract telemetry packets. The process involves the following steps:

1. **Input Source Selection**: The user can choose between decoding data from an audio file or a UDP stream. The audio file is typically a recording of a satellite signal, while the UDP stream is a real-time data feed.

2. **Signal Processing**: If an audio file is selected, the software reads the WAV file and converts the audio signal into a bitstream. For UDP streams, the software listens to the specified port and processes incoming data packets.

3. **Bit Decoding**: The bitstream is then processed to detect synchronization words and extract telemetry packets. The software supports multiple protocols, such as NGHam and AX100-Mode5, which are used to decode the packets.

4. **Packet Decoding**: Once the packets are extracted, they are decoded according to the satellite's configuration (stored in JSON files). The decoded data is then displayed in the GUI and can be saved to a log file.

5. **Output**: The decoded data is displayed in the GUI, and users can also send the data to a remote server for visualization or further processing.

Using the Software
------------------

1. **Launch the Application**: After installation, launch the SpaceLab Decoder.

2. **Select a Satellite**: From the main window, select the satellite you want to decode from the dropdown menu. The satellite configurations are loaded from JSON files.

3. **Choose the Input Source**:

   * **Audio File**: If you have a recorded audio file (e.g., WAV), select the "Audio File" option and choose the file using the file chooser.
   * **UDP Stream**: If you want to decode real-time data, select the "UDP" option and enter the UDP address and port.

4. **Start Decoding**: Click the "Decode" button to start the decoding process. The software will process the input data and display the decoded packets in the main window.

5. **View Decoded Data**: The decoded packets will be displayed in the text view. You can also view the event log, which records the decoding process.

6. **Plot Spectrum**: If you are using an audio file, you can plot the spectrum of the signal by clicking the "Plot Spectrum" button. This will display the signal's amplitude and frequency over time.

7. **Save Logs**: The decoded packets and event logs can be saved to a CSV file for further analysis. Use the logfile chooser button to specify the output file location.

8. **Connect to a Remote Server**: If you want to send the decoded data to a remote server for visualization, enter the server's address and port in the "Output" section and click "Connect".

9. **Stop Decoding**: To stop the decoding process, click the "Stop" button. This will halt the decoding and re-enable the input controls.

Configuraton
------------

The software allows you to configure general preferences, such as your callsign, location, and country. To access the preferences, click the "Preferences" button in the main window. You can also reset the preferences to their default values.

About
-----

To view information about the software, including the version and license, click the "About" button in the toolbar.

Using an SDR
------------

If an RTL-SDR v3 or v4 is used to receive signals, the internal bias tee must be disabled. This can be done manually using the command:

.. code-block:: bash

   rtl_biast -b 0

However, due to the implementation of the device drivers in the latest versions of the Linux kernel, the dvb_usb_rtl28xxu driver automatically enables the bias tee. Therefore, this driver must be permanently disabled. This can be done with the following terminal command:

.. code-block:: bash

   echo 'blacklist dvb_usb_rtl28xxu' | sudo tee --append /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf

After executing the command, the computer should be restarted.
