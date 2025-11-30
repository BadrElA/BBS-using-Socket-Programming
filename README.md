# BBS-using-Socket-Programming
Project 2 of Computer Networks


How to run:

On Linux / macOS / WSL 
    
    navigate to the correct folder
        cd Repos/BBS-using-Socket-Programming/server
    run
        g++ -std=c++17 server.cpp -lpthread -o server
        ./server

On Windows

    open Terminal
    install WSL
        wsl --install
    navigate to the code
        cd Repos/BBS-using-Socket-Programming/server
    install g++
        sudo apt update
        sudo apt install g++
    build server
        g++ -std=c++17 server.cpp -lpthread -o server
    run server
        ./server
    navigate to and run client.py (using any python IDE) (vs code on top)
    enter this in the terminal
        > %connect 127.0.0.1 65432
        > myname
        > %join
        > %post ; hello ; this is a test
        > %message 1

