#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <mutex>
#include <thread>
#include <sstream>
#include <chrono>
#include <ctime>
#include <algorithm>
#include <memory>
#include <cctype>

// POSIX sockets
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

// JSON library (nlohmann)
#include "json.hpp"

using json = nlohmann::json;

// Small helper: send all of a string to a socket
void send_all(int sock, const std::string &msg) {
    ::send(sock, msg.c_str(), msg.size(), 0);
}

// Safe trim (like Python .strip())
std::string trim(const std::string &s) {
    if (s.empty()) return s;

    size_t start = 0;
    while (start < s.size() &&
           std::isspace(static_cast<unsigned char>(s[start]))) {
        ++start;
    }
    if (start == s.size()) return "";  // all whitespace

    size_t end = s.size() - 1;
    while (end > start &&
           std::isspace(static_cast<unsigned char>(s[end]))) {
        --end;
    }
    return s.substr(start, end - start + 1);
}

// Get current time as "YYYY-MM-DD HH:MM:SS"
std::string current_timestamp() {
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    std::tm tm_buf{};
    localtime_r(&t, &tm_buf);

    char buf[20];
    std::strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &tm_buf);
    return std::string(buf);
}

class BulletinBoard {
public:
    BulletinBoard() = default;

    // Adds a user to the group. Doesn't allow if user is already in the group.
    void group_join(const std::string &username, int conn_fd) {
        std::lock_guard<std::mutex> lock(mtx_);
        if (members_.count(username) > 0) {
            throw std::runtime_error("user " + username +
                                     " is already a member of this group.");
        }
        members_[username] = conn_fd;
    }

    // Adds a message to the group and sends a thumbnail to everyone.
    void group_post(const std::string &username,
                    const std::string &subject,
                    const std::string &message) {
        std::lock_guard<std::mutex> lock(mtx_);

        if (members_.count(username) == 0) {
            throw std::runtime_error("User '" + username +
                                     "' is not a member of this group.");
        }

        int post_id = static_cast<int>(messages_.size()) + 1;
        std::string post_date = current_timestamp();

        std::ostringstream full_post;
        full_post << post_id << ", " << username << ", " << post_date << ", "
                  << subject << ", " << message;

        std::ostringstream thumb_post;
        thumb_post << post_id << ", " << username << ", " << post_date << ", "
                   << subject;

        std::string post = full_post.str();
        std::string thumb = thumb_post.str();

        messages_.push_back(post);

        // Broadcast thumbnail to all group members
        for (const auto &pair : members_) {
            int sock = pair.second;
            try {
                send_all(sock, thumb);
            } catch (...) {
                std::cerr << "Failed to send message to " << pair.first << "\n";
            }
        }
    }

    // Sends the list of users in the group.
    // If username is empty, send to all members. Otherwise, send to that user only.
    void group_users(const std::string &username = "") {
        std::lock_guard<std::mutex> lock(mtx_);

        if (members_.empty()) {
            return;
        }

        std::ostringstream oss;
        bool first = true;
        for (const auto &p : members_) {
            if (!first) oss << ", ";
            oss << p.first;
            first = false;
        }
        std::string user_list = oss.str();
        std::string msg = "users: " + user_list + " \n";

        if (username.empty()) {
            // broadcast
            for (const auto &p : members_) {
                send_all(p.second, msg);
            }
        } else {
            auto it = members_.find(username);
            if (it != members_.end()) {
                send_all(it->second, msg);
            }
        }
    }

    // Removes a user from the group
    void group_leave(const std::string &username) {
        std::lock_guard<std::mutex> lock(mtx_);

        auto it = members_.find(username);
        if (it == members_.end()) {
            throw std::runtime_error("User '" + username +
                                     "' is not a member of this group.");
        }

        members_.erase(it);
    }

    // Sends the requested message to the user
    void group_message(const std::string &username, int message_id) {
        std::lock_guard<std::mutex> lock(mtx_);

        auto it = members_.find(username);
        if (it == members_.end()) {
            throw std::runtime_error("User '" + username +
                                     "' is not a member of this group.");
        }

        int message_index = message_id - 1;
        int sock = it->second;

        if (message_index >= 0 &&
            message_index < static_cast<int>(messages_.size())) {
            send_all(sock, messages_[message_index]);
        } else {
            std::ostringstream oss;
            oss << "message not found, should be in the range 1 - "
                << messages_.size() << ", inclusive.\n";
            send_all(sock, oss.str());
        }
    }

    // Sends the previous two messages (or fewer if less exist) to the user
    void send_prev_two_messages(const std::string &username) {
        std::lock_guard<std::mutex> lock(mtx_);

        auto it = members_.find(username);
        if (it == members_.end()) {
            return; // not in group; in Python this can only be called after join
        }
        int sock = it->second;

        int count = static_cast<int>(messages_.size());
        if (count >= 2) {
            send_all(sock, messages_[count - 2] + "\n");
            send_all(sock, messages_[count - 1] + "\n");
        } else if (count == 1) {
            send_all(sock, messages_[0] + "\n");
        }
    }

    // Check if a username is in this group
    bool has_member(const std::string &username) const {
        std::lock_guard<std::mutex> lock(mtx_);
        return members_.count(username) > 0;
    }

private:
    std::vector<std::string> messages_;
    std::map<std::string, int> members_;
    mutable std::mutex mtx_;
};

class Server {
public:
    Server() {
        // Initialize default groups like Python version (using unique_ptr)
        bulletinboards_.emplace("default", std::make_unique<BulletinBoard>());
        bulletinboards_.emplace("group1",  std::make_unique<BulletinBoard>());
        bulletinboards_.emplace("group2",  std::make_unique<BulletinBoard>());
        bulletinboards_.emplace("group3",  std::make_unique<BulletinBoard>());
        bulletinboards_.emplace("group4",  std::make_unique<BulletinBoard>());
        bulletinboards_.emplace("group5",  std::make_unique<BulletinBoard>());
    }

    void run() {
        const char *HOST = "127.0.0.1";
        int PORT = 65432;

        int server_fd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (server_fd < 0) {
            perror("socket");
            return;
        }

        int opt = 1;
        if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR,
                       &opt, sizeof(opt)) < 0) {
            perror("setsockopt");
        }

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(PORT);
        addr.sin_addr.s_addr = inet_addr(HOST);

        if (bind(server_fd,
                 reinterpret_cast<sockaddr*>(&addr),
                 sizeof(addr)) < 0) {
            perror("bind");
            close(server_fd);
            return;
        }

        if (listen(server_fd, SOMAXCONN) < 0) {
            perror("listen");
            close(server_fd);
            return;
        }

        std::cout << "server started on host " << HOST
                  << " and port " << PORT << "\n";

        while (true) {
            sockaddr_in client_addr{};
            socklen_t client_len = sizeof(client_addr);
            int client_fd = accept(server_fd,
                                   reinterpret_cast<sockaddr*>(&client_addr),
                                   &client_len);
            if (client_fd < 0) {
                perror("accept");
                continue;
            }

            std::cout << "connected\n";
            std::thread(&Server::handle_client, this, client_fd).detach();
        }
    }

private:
    // map of group name -> BulletinBoard instance (owned via unique_ptr)
    std::map<std::string, std::unique_ptr<BulletinBoard>> bulletinboards_;
    std::mutex boards_mtx_;  // protect access to bulletinboards_ structure

    bool username_exists_anywhere(const std::string &username) {
        std::lock_guard<std::mutex> lock(boards_mtx_);
        for (auto &pair : bulletinboards_) {
            if (pair.second->has_member(username)) {
                return true;
            }
        }
        return false;
    }

    // Receive one "chunk" from client (up to 1024 bytes)
    // This roughly mimics conn.recv(1024) from Python.
    std::string recv_request(int client_fd) {
        char buf[1024];
        ssize_t n = recv(client_fd, buf, sizeof(buf), 0);
        if (n <= 0) {
            return "";
        }
        return std::string(buf, buf + n);
    }

    void handle_client(int client_fd) {
        // Ask for username
        send_all(client_fd, "Enter a username: \n");

        std::string username;
        {
            char buf[1024];
            ssize_t n = recv(client_fd, buf, sizeof(buf), 0);
            if (n <= 0) {
                close(client_fd);
                return;
            }
            username = trim(std::string(buf, buf + n));
        }

        // Check uniqueness across all groups
        while (username_exists_anywhere(username)) {
            send_all(client_fd,
                     "username already exists, please choose another username: \n");
            char buf[1024];
            ssize_t n = recv(client_fd, buf, sizeof(buf), 0);
            if (n <= 0) {
                close(client_fd);
                return;
            }
            username = trim(std::string(buf, buf + n));
        }

        // Main loop
        while (true) {
            std::string req_str = recv_request(client_fd);
            if (req_str.empty()) {
                break; // disconnected
            }

            req_str = trim(req_str);
            std::cout << "received request: " << req_str << std::endl;

            json request;
            try {
                request = json::parse(req_str);
            } catch (...) {
                // invalid JSON or partial packet
                continue;
            }

            std::string command;
            try {
                command = request.at("command").get<std::string>();
            } catch (...) {
                continue;
            }

            try {
                if (command == "%groupjoin") {
                    std::string group = request.at("group").get<std::string>();

                    BulletinBoard *board = get_board(group);
                    if (!board) {
                        std::string msg = "Error: Group '" + group +
                                          "' does not exist.\n";
                        send_all(client_fd, msg);
                        continue;
                    }

                    board->group_join(username, client_fd);
                    board->group_users();                 // broadcast users
                    board->send_prev_two_messages(username);

                } else if (command == "%grouppost") {
                    std::string group =
                        request.at("group").get<std::string>();
                    std::string subject =
                        request.at("subject").get<std::string>();
                    std::string message =
                        request.at("message").get<std::string>();

                    BulletinBoard *board = get_board(group);
                    if (!board) {
                        std::string msg = "Error: Group '" + group +
                                          "' does not exist.\n";
                        send_all(client_fd, msg);
                        continue;
                    }

                    board->group_post(username, subject, message);

                } else if (command == "%groupusers") {
                    std::string group =
                        request.at("group").get<std::string>();
                    BulletinBoard *board = get_board(group);
                    if (!board) {
                        std::string msg = "Error: Group '" + group +
                                          "' does not exist.\n";
                        send_all(client_fd, msg);
                        continue;
                    }
                    board->group_users(username);

                } else if (command == "%groupleave") {
                    std::string group =
                        request.at("group").get<std::string>();
                    BulletinBoard *board = get_board(group);
                    if (!board) {
                        std::string msg = "Error: Group '" + group +
                                          "' does not exist.\n";
                        send_all(client_fd, msg);
                        continue;
                    }

                    board->group_leave(username);
                    board->group_users(); // broadcast updated list

                } else if (command == "%groupmessage") {
                    std::string group =
                        request.at("group").get<std::string>();
                    // NOTE: Python client sends this as an int
                    int message_id =
                        request.at("message_id").get<int>();

                    BulletinBoard *board = get_board(group);
                    if (!board) {
                        std::string msg = "Error: Group '" + group +
                                          "' does not exist.\n";
                        send_all(client_fd, msg);
                        continue;
                    }

                    board->group_message(username, message_id);

                } else if (command == "%exit") {
                    // Remove user from any groups they’re in
                    {
                        std::lock_guard<std::mutex> lock(boards_mtx_);
                        for (auto &pair : bulletinboards_) {
                            try {
                                pair.second->group_leave(username);
                            } catch (...) {
                                // ignore if not in group
                            }
                        }
                    }
                    break;

                } else if (command == "%groups") {
                    std::string groups_list;
                    {
                        std::lock_guard<std::mutex> lock(boards_mtx_);
                        bool first = true;
                        for (auto &pair : bulletinboards_) {
                            if (!first) groups_list += ", ";
                            groups_list += pair.first;
                            first = false;
                        }
                    }
                    std::string msg =
                        "available groups: " + groups_list;
                    send_all(client_fd, msg);
                }

            } catch (const std::runtime_error &e) {
                std::string msg = std::string("Error: ") +
                                  e.what() + "\n";
                send_all(client_fd, msg);
            } catch (...) {
                // generic failure: just drop
            }
        }

        close(client_fd);
    }

    // Helper to access a board safely
    BulletinBoard* get_board(const std::string &group) {
        std::lock_guard<std::mutex> lock(boards_mtx_);
        auto it = bulletinboards_.find(group);
        if (it == bulletinboards_.end()) return nullptr;
        return it->second.get();
    }
};

int main() {
    Server server;
    server.run();
    return 0;
}
