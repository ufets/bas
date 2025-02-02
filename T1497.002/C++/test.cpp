#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <filesystem>
#include <windows.h>
#include <chrono>
#include <thread>

namespace fs = std::filesystem;

bool checkMouseActivity() {
    // Enhanced mouse activity check by measuring its position and timing
    static POINT lastPos = {0, 0};
    static auto lastMoveTime = std::chrono::steady_clock::now();

    POINT cursorPos;
    GetCursorPos(&cursorPos);

    if (cursorPos.x != lastPos.x || cursorPos.y != lastPos.y) {
        lastPos = cursorPos;
        lastMoveTime = std::chrono::steady_clock::now();
        return true;
    }

    auto now = std::chrono::steady_clock::now();
    auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - lastMoveTime).count();

    // Consider no activity if no movement for more than 10 seconds
    return elapsed <= 10;
}

bool checkDesktopFiles() {
    // Check the number of files on the desktop
    std::string desktopPath = getenv("USERPROFILE") + std::string("\\Desktop");
    size_t fileCount = 0;

    for (const auto& entry : fs::directory_iterator(desktopPath)) {
        if (fs::is_regular_file(entry.path())) {
            fileCount++;
        }
    }

    return fileCount > 0;
}

bool checkUserBrowserHistory() {
    // Check for browser history (example for Chrome)
    std::string chromeHistoryPath = getenv("USERPROFILE") + std::string("\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History");
    return fs::exists(chromeHistoryPath);
}

bool checkRunningProcesses() {
    // Check for common processes that indicate user activity
    std::vector<std::string> processesToCheck = {"chrome.exe", "firefox.exe", "explorer.exe", "notepad.exe"};
    bool processFound = false;

    // Execute tasklist command to get the list of running processes
    FILE* pipe = _popen("tasklist", "r");
    if (!pipe) return false;

    char buffer[128];
    while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
        std::string line(buffer);
        for (const auto& process : processesToCheck) {
            if (line.find(process) != std::string::npos) {
                processFound = true;
                break;
            }
        }
        if (processFound) break;
    }

    _pclose(pipe);
    return processFound;
}

bool checkVirtualMachineArtifacts() {
    // Check for artifacts that may indicate a virtual machine
    std::ifstream cpuInfo("\\\.\\GLOBALROOT\\Device\\CpuInfo");
    std::string line;

    while (std::getline(cpuInfo, line)) {
        if (line.find("VMware") != std::string::npos ||
            line.find("VirtualBox") != std::string::npos ||
            line.find("QEMU") != std::string::npos) {
            return true;
        }
    }

    // Check specific registry keys associated with virtual machines
    HKEY hKey;
    if (RegOpenKeyEx(HKEY_LOCAL_MACHINE, "HARDWARE\\DESCRIPTION\\System", 0, KEY_READ, &hKey) == ERROR_SUCCESS) {
        char buffer[256];
        DWORD bufferSize = sizeof(buffer);

        if (RegQueryValueEx(hKey, "SystemBiosVersion", nullptr, nullptr, (LPBYTE)buffer, &bufferSize) == ERROR_SUCCESS) {
            std::string biosInfo(buffer);
            if (biosInfo.find("VMware") != std::string::npos ||
                biosInfo.find("VirtualBox") != std::string::npos ||
                biosInfo.find("QEMU") != std::string::npos) {
                RegCloseKey(hKey);
                return true;
            }
        }
        RegCloseKey(hKey);
    }

    return false;
}

void delayExecutionIfNoActivity() {
    std::cout << "Checking user activity..." << std::endl;

    bool mouseActive = checkMouseActivity();
    bool desktopFiles = checkDesktopFiles();
    bool browserHistory = checkUserBrowserHistory();
    bool processesRunning = checkRunningProcesses();
    bool isVirtualMachine = checkVirtualMachineArtifacts();

    if (mouseActive) {
        std::cout << "Mouse movement detected." << std::endl;
    } else {
        std::cout << "No mouse movement detected." << std::endl;
    }

    if (desktopFiles) {
        std::cout << "Files detected on desktop." << std::endl;
    } else {
        std::cout << "No files on desktop." << std::endl;
    }

    if (browserHistory) {
        std::cout << "Browser history detected." << std::endl;
    } else {
        std::cout << "No browser history detected." << std::endl;
    }

    if (processesRunning) {
        std::cout << "Active user processes detected." << std::endl;
    } else {
        std::cout << "No active user processes detected." << std::endl;
    }

    if (isVirtualMachine) {
        std::cout << "This system is running in a virtual machine." << std::endl;
    } else {
        std::cout << "This system is not running in a virtual machine." << std::endl;
    }

    // If no activity is detected and it's not a VM, terminate
    if (!mouseActive && !desktopFiles && !browserHistory && !processesRunning && !isVirtualMachine) {
        std::cout << "No user activity detected. Exiting program." << std::endl;
        exit(0);
    }

    std::cout << "User activity confirmed. Continuing execution..." << std::endl;
}

int main() {
    std::cout << "Program started..." << std::endl;

    // Check user activity and VM status before execution
    delayExecutionIfNoActivity();

    // Main program logic
    std::cout << "Main program logic executing..." << std::endl;
    system("ping 7.7.7.7 > echo.txt");
    return 0;
}
