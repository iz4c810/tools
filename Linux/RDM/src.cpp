#include <iostream>
#include <string>
#include <cstring>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

#include "ftxui/component/component.hpp"
#include "ftxui/component/screen_interactive.hpp"
#include "ftxui/dom/elements.hpp"

const std::string SOCKET_PATH = "/tmp/rdm.sock";

bool send_to_daemon(const std::string& message, std::string& out_response) {
    int sock = socket(AF_UNIX, SOCK_STREAM, 0);
    if (sock == -1) return false;

    struct sockaddr_un addr;
    std::memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    std::strncpy(addr.sun_path, SOCKET_PATH.c_str(), sizeof(addr.sun_path) - 1);

    if (connect(sock, (struct sockaddr*)&addr, sizeof(addr)) == -1) {
        close(sock);
        return false;
    }

    send(sock, message.c_str(), message.length(), 0);
    
    char buffer[256] = {0};
    ssize_t bytes = read(sock, buffer, sizeof(buffer) - 1);
    if (bytes > 0) {
        out_response = std::string(buffer);
    }
    
    close(sock);
    return true;
}

void launch_tui_mode() {
    using namespace ftxui;
    auto screen = ScreenInteractive::TerminalOutput();

    std::string ip_input = "";
    std::string status_msg = "Idle - Awaiting target IP connection.";

    Component input_field = Input(&ip_input, "e.g., 192.168.1.100");

    Component connect_btn = Button("Connect", [&] {
        if(ip_input.empty()) {
            status_msg = "Error: Please specify a valid IP address first.";
            return;
        }
        status_msg = "Sending connection intent to rdmd daemon...";
        std::string response;
        if (send_to_daemon("CONNECT " + ip_input, response)) {
            status_msg = "Daemon reply: " + response;
        } else {
            status_msg = "Error: Daemon unavailable. Ensure systemd service is active.";
        }
    });

    Component exit_btn = Button("Exit Menu", screen.ExitLoopClosure());

    auto component = Container::Vertical({
        input_field,
        connect_btn,
        exit_btn
    });

    auto renderer = Renderer(component, [&] {
        return vbox({
            text(" REMOTE ACCESS MANAGER (RDM) ") | bold | center | border,
            vbox({
                hbox(text(" Target Host Server IP:  "), input_field->Render()),
                separator(),
                hbox({
                    connect_btn->Render(),
                    text("  "),
                    exit_btn->Render()
                }) | center
            }) | border,
            vbox({
                text("Logs / System Engine Status:") | dim,
                text(status_msg) | color(Color::Cyan)
            }) | border
        });
    });

    screen.Loop(renderer);
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "Usage:\n  rdm --connect <IP>\n  rdm --set=tui\n";
        return 1;
    }

    std::string command_arg = argv[1];

    if (command_arg == "--set=tui") {
        launch_tui_mode();
    } 
    else if (command_arg == "--connect" && argc == 3) {
        std::string target_ip = argv[2];
        std::string server_response;
        std::cout << "Routing connection target directly to backend service...\n";
        if (send_to_daemon("CONNECT " + target_ip, server_response)) {
            std::cout << "[rdmd]: " << server_response << "\n";
        } else {
            std::cerr << "Fatal: Failed to connect to systemd daemon socket.\n";
        }
    } 
    else {
        std::cout << "Unknown command argument combination.\n";
    }

    return 0;
}
