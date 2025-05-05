#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include <lm.h>       // Для работы с пользователями
#include <iphlpapi.h> // Для работы с сетью
#include <winsock2.h> // Для работы с сокетами (преобразование IP)
#include <iptypes.h>
#include <winreg.h>   // Для работы с реестром
#include <intrin.h>

#pragma comment(lib, "Netapi32.lib")
#pragma comment(lib, "Iphlpapi.lib")
#pragma comment(lib, "Ws2_32.lib")

// Функция для записи информации в файл
void write_to_file(const char *filename, const char *data) {
    FILE *file = fopen(filename, "a");
    if (file != NULL) {
        fprintf(file, "%s\n", data);
        fclose(file);
    } else {
        perror("Ошибка открытия файла");
    }
}

// Функция для определения производителя CPU
const char* get_cpu_vendor() {
    int cpuInfo[4] = { -1 };
    char cpuVendor[13];
    __cpuid(cpuInfo, 0);
    memcpy(cpuVendor, &cpuInfo[1], 4);
    memcpy(cpuVendor + 4, &cpuInfo[3], 4);
    memcpy(cpuVendor + 8, &cpuInfo[2], 4);
    cpuVendor[12] = '\0';
    return _strdup(cpuVendor); // Используем _strdup для выделения памяти
}

// Функция для проверки на виртуальную машину (упрощенная)
BOOL is_virtual_machine() {
    int cpuInfo[4] = { -1 };
    __cpuid(cpuInfo, 1);
    return (cpuInfo[2] & (1 << 31)); // Проверяем 31-й бит регистра ECX
}

void get_user_info() {
    LPUSER_INFO_0 pUserInfo = NULL;
    NET_API_STATUS res;
    DWORD entriesread = 0;
    DWORD totalentries = 0;
    DWORD resumehandle = 0;
    DWORD i;
    char buffer[256];

    res = NetUserEnum(NULL, 0, FILTER_NORMAL_ACCOUNT, (LPBYTE*)&pUserInfo, MAX_PREFERRED_LENGTH, &entriesread, &totalentries, &resumehandle);

    if (res == NERR_Success || res == ERROR_MORE_DATA) {
        for (i = 0; i < entriesread; i++) {
            sprintf(buffer, "Пользователь: %s", pUserInfo[i].usri0_name);
            write_to_file("system_info.txt", buffer);
        }
        NetApiBufferFree(pUserInfo);
    } else {
        sprintf(buffer, "Ошибка получения информации о пользователях: %d", res);
        write_to_file("system_info.txt", buffer);
    }
}

// Функция для получения сетевой информации (адаптеры и IP)
void get_network_info() {
    PIP_ADAPTER_INFO pAdapterInfo;
    PIP_ADAPTER_INFO pAdapter = NULL;
    ULONG ulOutBufLen = sizeof(IP_ADAPTER_INFO);
    DWORD dwRetVal = 0;
    char buffer[256];

    pAdapterInfo = (IP_ADAPTER_INFO*)malloc(sizeof(IP_ADAPTER_INFO));
    if (pAdapterInfo == NULL) {
        write_to_file("system_info.txt", "Ошибка выделения памяти для IP_ADAPTER_INFO");
        return;
    }

    if ((dwRetVal = GetAdaptersInfo(pAdapterInfo, &ulOutBufLen)) == ERROR_BUFFER_OVERFLOW) {
        free(pAdapterInfo);
        pAdapterInfo = (IP_ADAPTER_INFO*)malloc(ulOutBufLen);
        if (pAdapterInfo == NULL) {
            write_to_file("system_info.txt", "Ошибка повторного выделения памяти для IP_ADAPTER_INFO");
            return;
        }
        dwRetVal = GetAdaptersInfo(pAdapterInfo, &ulOutBufLen);
    }

    if (dwRetVal == NO_ERROR) {
        pAdapter = pAdapterInfo;
        while (pAdapter) {
            sprintf(buffer, "Адаптер: %s", pAdapter->Description);
            write_to_file("system_info.txt", buffer);
            sprintf(buffer, "IP-адрес: %s", pAdapter->IpAddressList.IpAddress.String);
            write_to_file("system_info.txt", buffer);
            sprintf(buffer, "Маска подсети: %s", pAdapter->IpAddressList.IpMask.String);
            write_to_file("system_info.txt", buffer);
            pAdapter = pAdapter->Next;
        }
    } else {
        sprintf(buffer, "Ошибка получения информации об адаптерах: %d", dwRetVal);
        write_to_file("system_info.txt", buffer);
    }

    if (pAdapterInfo)
        free(pAdapterInfo);
}

// Функция для получения маршрутов
void get_route_info() {
    MIB_IPFORWARDTABLE* pIpForwardTable = NULL;
    DWORD dwSize = 0;
    DWORD dwResult = 0;
    char buffer[256];

    dwResult = GetIpForwardTable(NULL, &dwSize, TRUE);
    if (dwResult == ERROR_INSUFFICIENT_BUFFER) {
        pIpForwardTable = (MIB_IPFORWARDTABLE*)malloc(dwSize);
        if (pIpForwardTable == NULL) {
            write_to_file("system_info.txt", "Ошибка выделения памяти для таблицы маршрутов");
            return;
        }
        dwResult = GetIpForwardTable(pIpForwardTable, &dwSize, TRUE);
    }

    if (dwResult == NO_ERROR) {
        for (DWORD i = 0; i < pIpForwardTable->dwNumEntries; i++) {
            sprintf(buffer, "Назначение: %u, Маска: %u, Шлюз: %u, Метрика: %u",
                    pIpForwardTable->table[i].dwForwardDest,
                    pIpForwardTable->table[i].dwForwardMask,
                    pIpForwardTable->table[i].dwForwardNextHop,
                    pIpForwardTable->table[i].dwForwardMetric1);
            write_to_file("system_info.txt", buffer);
        }
    } else {
        sprintf(buffer, "Ошибка получения таблицы маршрутов: %d", dwResult);
        write_to_file("system_info.txt", buffer);
    }

    if (pIpForwardTable)
        free(pIpForwardTable);
}

// Функция для чтения значения из реестра
void get_registry_value(HKEY hKey, const char* subKey, const char* valueName) {
    HKEY hSubKey;
    DWORD dwType;
    BYTE data[1024];
    DWORD dwSize = sizeof(data);
    char buffer[256];

    if (RegOpenKeyEx(hKey, subKey, 0, KEY_READ, &hSubKey) == ERROR_SUCCESS) {
        if (RegQueryValueEx(hSubKey, valueName, NULL, &dwType, data, &dwSize) == ERROR_SUCCESS) {
            if (dwType == REG_SZ) {
                sprintf(buffer, "Реестр (%s\\%s): %s", subKey, valueName, data);
                write_to_file("system_info.txt", buffer);
            }
        }
        RegCloseKey(hSubKey);
    }
}


int main() {
    SYSTEM_INFO sysInfo;
    MEMORYSTATUSEX memStatus;
    OSVERSIONINFOEX osInfo;
    BOOL bOsVersionInfoEx;

    // Получаем информацию о системе
    GetSystemInfo(&sysInfo);

    // Получаем информацию о памяти
    memStatus.dwLength = sizeof(memStatus);
    GlobalMemoryStatusEx(&memStatus);

    // Получаем информацию о версии ОС
    ZeroMemory(&osInfo, sizeof(OSVERSIONINFOEX));
    osInfo.dwOSVersionInfoSize = sizeof(OSVERSIONINFOEX);

    bOsVersionInfoEx = GetVersionEx((OSVERSIONINFO *)&osInfo);
    if(bOsVersionInfoEx == 0) {
       osInfo.dwOSVersionInfoSize = sizeof (OSVERSIONINFO);
       if ( GetVersionEx ((OSVERSIONINFO *)&osInfo) == 0 )
       {
           printf ("Error getting OS version\n");
           return 1;
       }
    }


    // Открываем файл для записи (перезаписываем, если существует)
    FILE *file = fopen("system_info.txt", "w");
    if (file == NULL) {
        perror("Ошибка создания файла");
        return 1;
    }
    fclose(file);

    const char *cpuVendor = get_cpu_vendor();
    write_to_file("system_info.txt", "--- Информация о системе ---");
    write_to_file("system_info.txt", cpuVendor);
    free((void*)cpuVendor); // Освобождаем выделенную память

    char buffer[256];

    sprintf(buffer, "Количество процессоров: %d", sysInfo.dwNumberOfProcessors);
    write_to_file("system_info.txt", buffer);

    sprintf(buffer, "Тип процессора: %d", sysInfo.wProcessorArchitecture);
    write_to_file("system_info.txt", buffer);

    sprintf(buffer, "Объем памяти (физической): %llu МБ", memStatus.ullTotalPhys / (1024 * 1024));
    write_to_file("system_info.txt", buffer);

    sprintf(buffer, "Версия ОС: %d.%d (Build %d)", osInfo.dwMajorVersion, osInfo.dwMinorVersion, osInfo.dwBuildNumber);
    write_to_file("system_info.txt", buffer);

    if (is_virtual_machine()) {
        write_to_file("system_info.txt", "Система запущена на виртуальной машине.");
    } else {
        write_to_file("system_info.txt", "Система НЕ запущена на виртуальной машине.");
    }

    write_to_file("system_info.txt", "--- Информация о пользователях ---");
    get_user_info();

    write_to_file("system_info.txt", "--- Сетевая информация ---");
    get_network_info();

    write_to_file("system_info.txt", "--- Таблица маршрутов ---");
    get_route_info();

    write_to_file("system_info.txt", "--- Информация из реестра ---");
    get_registry_value(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion", "ProductName");
    get_registry_value(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion", "CurrentBuildNumber");
    get_registry_value(HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Control\\ComputerName\\ComputerName", "ComputerName");

    write_to_file("system_info.txt", "--- Конец информации ---");

    printf("Информация записана в файл system_info.txt\n");

    return 0;
}