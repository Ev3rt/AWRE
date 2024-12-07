#include <gba_types.h>

/*
The below macro is designed so that it matches the call to InitUnknownWramStructure.
When the full game has been decompiled, all source files can be linked together, and
except for removing this header file no changes are required.
*/
#define InitUnknownWramStructure(param_1, param_2, count) \
    asm volatile(                                         \
        "ldr r0, [%0]\n"                                  \
        "ldr r1, [%1]\n"                                  \
        "mov r2, %2\n"                                    \
        "b 0x0807AF94\n"                                  \
        : /* No outputs */                                \
        : "r"(param_1), "r"(param_2), "r"(count)          \
        : "r0", "r1", "r2")
