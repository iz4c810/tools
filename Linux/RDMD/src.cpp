#include <iostream>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <string>
#include <cstring>

const std::string SOCKET_PATH = "/tmp/rdm.sock";

void handle_client(int client_fd) {
    char buffer[256] = {0};
    ssize_t bytes_read = read(client_fd, buffer, sizeof(buffer) - 1);
    if (bytes_read > 0) {
        std::string command(buffer);
        std::cout << "[Daemon] Received command: " << command << std::endl;
        
        if (command.rfind("CONNECT ", 0) == 0) {
            std::string ip = command.substr(8);
            std::cout << "[Daemon] Connection request received for IP: " << ip << std::endl;
            
            // This is where you will trigger your connection utility later!
            
            write(client_fd, "SUCCESS: Connection initiated", 29);
        } else {
            write(client_fd, "ERROR: Unknown command", 22);
        }
    }
    close(client_fd);
}

int main() {
    int server_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (server_fd == -1) {
        std::cerr << "Failed to create socket\n";
        return 1;
    }

    struct sockaddr_un addr;
    std::memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    std::strncpy(addr.sun_path, SOCKET_PATH.c_str(), sizeof(addr.sun_path) - 1);

    unlink(SOCKET_PATH.c_str());

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) == -1) {
        std::cerr << "Failed to bind socket\n";
        return 1;
    }

    if (listen(server_fd, 5) == -1) {
        std::cerr << "Failed to listen\n";
        return 1;
    }

    std::cout << "[Daemon] Remote Access Manager daemon listening on " << SOCKET_PATH << "..." << std::endl;

    while (true) {
        int client_fd = accept(server_fd, nullptr, nullptr);
        if (client_fd != -1) {
            handle_client(client_fd);
        }
    }

    close(server_fd);
    return 0;
}

