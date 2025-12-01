# Makefile for BBS-using-Socket-Programming
# CONFIG
CXX      := g++
CXXFLAGS := -std=c++17
LDFLAGS  := -lpthread
TARGET   := server
SRC      := server.cpp

.PHONY: all setup build server client gui clean

# build
all: build

# Compile server
build: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) $(LDFLAGS) -o $(TARGET)

# Build + run the server (terminal for the server)
server: build
	./$(TARGET)


client: gui

gui:
	cd ../client && python3 gui_client.py

# Clean built binary
clean:
	rm -f $(TARGET)