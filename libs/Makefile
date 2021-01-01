TARGET=libngham.so

ifndef BUILD_DIR
	BUILD_DIR=$(CURDIR)
endif

CC=gcc
CFLAGS=-c -fPIC -I$(CURDIR)/ngham/ -o

$(BUILD_DIR)/$(TARGET): $(BUILD_DIR)/ccsds_scrambler.o $(BUILD_DIR)/crc_ccitt.o $(BUILD_DIR)/decode_rs_char.o $(BUILD_DIR)/encode_rs_char.o $(BUILD_DIR)/init_rs_char.o $(BUILD_DIR)/ngham.o $(BUILD_DIR)/ngham_extension.o $(BUILD_DIR)/ngham_packets.o $(BUILD_DIR)/platform.o
	$(CC) -shared -fPIC -Wall -o $(BUILD_DIR)/$(TARGET) *.o -lc

$(BUILD_DIR)/ccsds_scrambler.o: ngham/ccsds_scrambler.c ngham/ccsds_scrambler.h
	$(CC) $(CFLAGS) $@ $<

$(BUILD_DIR)/crc_ccitt.o: ngham/crc_ccitt.c ngham/crc_ccitt.h
	$(CC) $(CFLAGS) $@ $<

$(BUILD_DIR)/fec.o: ngham/fec-3.0.1/fec.c ngham/fec-3.0.1/fec.h
	$(CC) $(CFLAGS) $@ $<

$(BUILD_DIR)/decode_rs_char.o: ngham/fec-3.0.1/decode_rs_char.c
	$(CC) $(CFLAGS) $@ $<

$(BUILD_DIR)/encode_rs_char.o: ngham/fec-3.0.1/encode_rs_char.c
	$(CC) $(CFLAGS) $@ $<

$(BUILD_DIR)/init_rs_char.o: ngham/fec-3.0.1/init_rs_char.c
	$(CC) $(CFLAGS) $@ $<

$(BUILD_DIR)/ngham.o: ngham/ngham.c ngham/ngham.h
	$(CC) $(CFLAGS) $@ $<

$(BUILD_DIR)/ngham_extension.o: ngham/ngham_extension.c ngham/ngham_extension.h
	$(CC) $(CFLAGS) $@ $<

$(BUILD_DIR)/ngham_packets.o: ngham/ngham_packets.c ngham/ngham_packets.h
	$(CC) $(CFLAGS) $@ $<

$(BUILD_DIR)/platform.o: ngham/platform/platform.c ngham/platform/platform.h
	$(CC) $(CFLAGS) $@ $<

clean:
	rm $(BUILD_DIR)/*.o $(BUILD_DIR)/$(TARGET)
