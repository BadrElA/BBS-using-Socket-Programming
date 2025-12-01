# BBS-using-Socket-Programming
Project 2 of Computer Networks

Group Members: Badr | Jason Galanie | Colin Hill

Required dependencies:

    WSL (windows only)
    g++
    make

How to install dependencies:

    Windows users only:
    open Terminal
    install WSL (first time only)
        wsl --install   
    Run all commands from WSL bash

    open Terminal (WSL bash for Windows users)
    Navigate to server path
        cd Repos/BBS-using-Socket-Programming/server
    install g++ and make (first time only)
        sudo apt update
        sudo apt install -y g++
        sudo apt install -y make
    
START HERE IF WSL, g++ and make ARE ALREADY INSTALLED

How to build and run server:
    
    in terminal/WSL at BBS-using-Socket-Programming/server:
        make

Run Client:

    Navigate to and run gui_client.py 
    
    To Connect:
        Enter Host (usually 127.0.0.1)
        Enter Port (65432)
        Enter a Username
        Click Connect

    To join a Group:
    Enter a group name (ex: default)
    Click Join Group

    To post a Message:
        Enter a Subject
        Enter your Message
        Click Post

    To read a Message:
        Enter group name
        Enter the Message ID
        Click Get Message

    Other Actions:
        List Users → shows users in the current group
        List All Groups → shows all groups on the server
        Exit (Server) → cleanly disconnects   


