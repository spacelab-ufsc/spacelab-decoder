TARGET=spacelab-decoder
LIB_NGHAM_TARGET=libngham.so
LIB_NGHAM_FSAT_TARGET=libngham_fsat.so

ifndef BUILD_DIR
	BUILD_DIR=$(CURDIR)/build/
endif

CC=gcc
INC=`pkg-config --cflags --libs python3`
LDFLAGS=`/usr/bin/python3-config --embed --ldflags`

all:
	mkdir -p $(BUILD_DIR)
	$(CC) $(INC) main.c -o $(BUILD_DIR)/$(TARGET) $(LDFLAGS)
	$(MAKE) BUILD_DIR=$(BUILD_DIR) -C libs

install:
	cp -r spacelab-decoder /usr/share/
	cp spacelab-decoder/icon/spacelab_decoder_256x256.png /usr/share/icons/spacelab_decoder_256x256.png
	install -m 0755 $(BUILD_DIR)/$(TARGET) /usr/bin/$(TARGET)
	install -m 0755 $(BUILD_DIR)/$(LIB_NGHAM_TARGET) /usr/lib/$(LIB_NGHAM_TARGET)
	install -m 0755 $(BUILD_DIR)/$(LIB_NGHAM_FSAT_TARGET) /usr/lib/$(LIB_NGHAM_FSAT_TARGET)

uninstall:
	rm -r /usr/share/spacelab-decoder
	rm /usr/share/icons/spacelab_decoder_256x256.png
	rm /usr/bin/$(TARGET)
	rm /usr/lib/$(LIB_NGHAM_TARGET)
	rm /usr/lib/$(LIB_NGHAM_FSAT_TARGET)

clean:
	rm $(BUILD_DIR)/$(TARGET) $(BUILD_DIR)/*.o $(BUILD_DIR)/*.so
