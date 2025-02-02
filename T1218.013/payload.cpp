#include <windows.h>
#include <stdio.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD fdwReason, LPVOID lpReserved) {
    switch (fdwReason)
    {
        case DLL_PROCESS_ATTACH:
            MessageBoxA(NULL, "DLL successfully injected", "DLL Injection", MB_OK | MB_ICONINFORMATION); 
        case DLL_PROCESS_DETACH:
            printf("DETACH DLL\n");
            break;
        case DLL_THREAD_ATTACH:
            break;
        case DLL_THREAD_DETACH:
            break;
    }
    return TRUE; // succesful
}