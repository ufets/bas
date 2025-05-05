#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dlfcn.h>
#include <sys/mman.h>
#include <sys/auxv.h>
#include <sys/time.h>

// Size of one page (assumed vDSO page)
#define PAGE_SIZE 4096

int main(void) {
    // 1. Locate the base of the vDSO via auxv
    void *vdso_base = (void *) getauxval(AT_SYSINFO_EHDR);
    if (!vdso_base) {
        perror("getauxval");
        return 1;
    }

    // 2. Resolve the address of __vdso_gettimeofday
    void *orig_gtd = dlsym(RTLD_DEFAULT, "__vdso_gettimeofday");
    if (!orig_gtd) {
        fprintf(stderr, "dlsym: %s\n", dlerror());
        return 1;
    }

    // 3. Allocate an executable trampoline
    void *tramp = mmap(NULL, PAGE_SIZE,
                       PROT_READ | PROT_WRITE | PROT_EXEC,
                       MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
    if (tramp == MAP_FAILED) {
        perror("mmap");
        return 1;
    }

    // 4. Build trampoline: a jump back to original stub+5
    unsigned char tramp_code[16] = {
        0xE9,                   // JMP rel32
        0,0,0,0,                // placeholder for offset
        // (optionally: your payload here)
    };
    // Compute displacement: (orig+5) - (tramp+5)
    intptr_t back_disp = ((unsigned char*)orig_gtd + 5) -
                         ((unsigned char*)tramp + 5);
    memcpy(&tramp_code[1], &back_disp, 4);
    memcpy(tramp, tramp_code, sizeof(tramp_code));

    // 5. Unprotect vDSO page, patch stub to JMP trampoline
    if (mprotect(vdso_base, PAGE_SIZE,
                 PROT_READ | PROT_WRITE | PROT_EXEC) < 0) {
        perror("mprotect RWX");
        return 1;
    }
    unsigned char patch[5] = { 0xE9 };
    intptr_t fwd_disp = (unsigned char*)tramp -
                        ((unsigned char*)orig_gtd + 5);
    memcpy(&patch[1], &fwd_disp, 4);
    memcpy(orig_gtd, patch, sizeof(patch));

    // Restore vDSO to read+exec only
    if (mprotect(vdso_base, PAGE_SIZE,
                 PROT_READ | PROT_EXEC) < 0) {
        perror("mprotect RX");
        return 1;
    }

    // 6. Invoke gettimeofday to trigger our hook
    struct timeval tv;
    gettimeofday(&tv, NULL);
    printf("Hijacked gettimeofday: %ld.%06ld\n",
           (long)tv.tv_sec, (long)tv.tv_usec);

    return 0;
}
