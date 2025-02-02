
#include <iostream>
#include <string>
#include <winsock2.h>
#include <ws2tcpip.h>

// Подключаем библиотеку Winsock
#pragma comment(lib, "Ws2_32.lib")

int main() {
    const std::string DOMAIN_NAME = "{{DOMAIN_NAME}}"; // Имя домена
    const int PORT = {{PORT}};                        // Порт
    const std::string USER_ID = "{{USER_ID}}";        // Идентификатор пользователя

    const std::string endpoint = "/api/executable_file_runned?q=" + USER_ID;
    const std::string host = DOMAIN_NAME + ":" + std::to_string(PORT);

    // Создание тела и заголовков запроса
    const std::string request =
        "POST " + endpoint + " HTTP/1.1\r\n" +
        "Host: " + host + "\r\n" +
        "Content-Length: 0\r\n" +  // Указываем, что тела у запроса нет
        "Connection: close\r\n" +
        "\r\n";
    std::cout << "request:\n" << request << std::endl;
    // Инициализация Winsock
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "Error init Winsock" << std::endl;
        return 1;
    }

    // Используем getaddrinfo для резолвинга доменного имени
    struct addrinfo hints{}, *result = nullptr;
    hints.ai_family = AF_INET;        // IPv4
    hints.ai_socktype = SOCK_STREAM; // TCP
    hints.ai_protocol = IPPROTO_TCP; // Протокол TCP

    int addrinfo_status = getaddrinfo(DOMAIN_NAME.c_str(), std::to_string(PORT).c_str(), &hints, &result);
    if (addrinfo_status != 0) {
        std::cerr << "Error resolving domain: " << DOMAIN_NAME << " (" << gai_strerror(addrinfo_status) << ")" << std::endl;
        WSACleanup();
        return 1;
    }

    // Создаем сокет
    SOCKET sock = socket(result->ai_family, result->ai_socktype, result->ai_protocol);
    if (sock == INVALID_SOCKET) {
        std::cerr << "Error create Winsock" << std::endl;
        freeaddrinfo(result);
        WSACleanup();
        return 1;
    }

    // Установка соединения с сервером
    if (connect(sock, result->ai_addr, static_cast<int>(result->ai_addrlen)) == SOCKET_ERROR) {
        std::cerr << "Error connect to server" << std::endl;
        closesocket(sock);
        freeaddrinfo(result);
        WSACleanup();
        return 1;
    }

    freeaddrinfo(result); // Очищаем память, выделенную getaddrinfo

    // Отправка запроса
    if (send(sock, request.c_str(), request.size(), 0) == SOCKET_ERROR) {
        std::cerr << "Error create request" << std::endl;
        closesocket(sock);
        WSACleanup();
        return 1;
    }

    // Чтение ответа от сервера
    char buffer[1024];
    std::string response;
    int bytes_read;
    while ((bytes_read = recv(sock, buffer, sizeof(buffer) - 1, 0)) > 0) {
        buffer[bytes_read] = '\0';
        response += buffer;
    }

    if (bytes_read == SOCKET_ERROR) {
        std::cerr << "Error read answer" << std::endl;
    } else {
        std::cout << "response:\n" << response << std::endl;
    }

    // Закрытие сокета
    closesocket(sock);
    WSACleanup();

    return 0;
}
