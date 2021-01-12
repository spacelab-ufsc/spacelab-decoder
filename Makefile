LIB_NGHAM_TARGET=libngham.so
LIB_NGHAM_FSAT_TARGET=libngham_fsat.so

ifndef BUILD_DIR
	BUILD_DIR=$(CURDIR)/build/
endif

all:
	mkdir -p $(BUILD_DIR)
	$(MAKE) BUILD_DIR=$(BUILD_DIR) -C libs
	cp $(BUILD_DIR)*.so spacelab_decoder/

install:
	install -m 0755 $(BUILD_DIR)/$(LIB_NGHAM_TARGET) /usr/lib/$(LIB_NGHAM_TARGET)
	install -m 0755 $(BUILD_DIR)/$(LIB_NGHAM_FSAT_TARGET) /usr/lib/$(LIB_NGHAM_FSAT_TARGET)

uninstall:
	rm /usr/lib/$(LIB_NGHAM_TARGET)
	rm /usr/lib/$(LIB_NGHAM_FSAT_TARGET)

clean:
	rm $(BUILD_DIR)/*.o $(BUILD_DIR)/*.so
