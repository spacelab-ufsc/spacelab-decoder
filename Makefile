LIB_NGHAM_TARGET=libngham.so
LIB_NGHAM_FSAT_TARGET=libngham_fsat.so

ifndef BUILD_DIR
	BUILD_DIR=$(CURDIR)
endif

all:
	$(MAKE) BUILD_DIR=$(BUILD_DIR) -C libs

install:
	install -m 0755 $(BUILD_DIR)/$(LIB_NGHAM_TARGET) /usr/local/lib/$(LIB_NGHAM_TARGET)
	install -m 0755 $(BUILD_DIR)/$(LIB_NGHAM_FSAT_TARGET) /usr/local/lib/$(LIB_NGHAM_FSAT_TARGET)

uninstall:
	rm /usr/local/lib/$(LIB_NGHAM_TARGET)
	rm /usr/local/lib/$(LIB_NGHAM_FSAT_TARGET)

clean:
	rm $(BUILD_DIR)/*.o $(BUILD_DIR)/*.so
