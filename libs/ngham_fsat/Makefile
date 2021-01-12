TARGET=libngham_fsat.so

ifndef BUILD_DIR
	BUILD_DIR=.
endif

CC=gcc
CFLAGS=-c -fPIC -o

$(BUILD_DIR)/$(TARGET): $(BUILD_DIR)/ccsds_scrambler_fsat.o $(BUILD_DIR)/crc_ccitt_fsat.o $(BUILD_DIR)/fec_fsat.o $(BUILD_DIR)/ngham_fsat.o $(BUILD_DIR)/ngham_extension_fsat.o $(BUILD_DIR)/ngham_packets_fsat.o $(BUILD_DIR)/platform_fsat.o
	$(CC) -shared -fPIC -Wall -o $(BUILD_DIR)/$(TARGET) $(BUILD_DIR)/ccsds_scrambler_fsat.o $(BUILD_DIR)/crc_ccitt_fsat.o $(BUILD_DIR)/fec_fsat.o $(BUILD_DIR)/ngham_fsat.o $(BUILD_DIR)/ngham_extension_fsat.o $(BUILD_DIR)/ngham_packets_fsat.o $(BUILD_DIR)/platform_fsat.o -lc

$(BUILD_DIR)/ccsds_scrambler_fsat.o: ccsds_scrambler.c ccsds_scrambler.h
	$(CC) $(CFLAGS) $@ $<

$(BUILD_DIR)/crc_ccitt_fsat.o: crc_ccitt.c crc_ccitt.h
	$(CC) $(CFLAGS) $@ $<

$(BUILD_DIR)/fec_fsat.o: fec.c fec.h
	$(CC) $(CFLAGS) $@ $<

$(BUILD_DIR)/ngham_fsat.o: ngham.c ngham.h
	$(CC) $(CFLAGS) $@ $<

$(BUILD_DIR)/ngham_extension_fsat.o: ngham_extension.c ngham_extension.h
	$(CC) $(CFLAGS) $@ $<

$(BUILD_DIR)/ngham_packets_fsat.o: ngham_packets.c ngham_packets.h
	$(CC) $(CFLAGS) $@ $<

$(BUILD_DIR)/platform_fsat.o: platform/platform.c platform/platform.h
	$(CC) $(CFLAGS) $@ $<

clean:
	rm $(BUILD_DIR)/*.o $(BUILD_DIR)/$(TARGET)
