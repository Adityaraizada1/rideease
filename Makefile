CXX ?= g++
CXXFLAGS ?= -std=c++17 -Wall -Wextra -pedantic -Iinclude

# Prefer the full Xcode SDK when it is installed. This avoids a broken or stale
# Command Line Tools SDK on some macOS installations, while remaining portable.
ifeq ($(shell uname -s),Darwin)
ifneq ($(wildcard /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk),)
CXXFLAGS += -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk
endif
endif

SOURCES := $(wildcard src/*.cpp)
TARGET := rideease

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) $(SOURCES) -o $(TARGET)

gui:
	python3 gui.py

web:
	open "http://localhost:8080" 2>/dev/null || true
	python3 web_gui.py 8080

clean:
	rm -f $(TARGET)

.PHONY: all clean gui web
