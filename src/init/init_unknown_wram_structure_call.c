#include <gba_types.h>
#include "functions.h"

// TODO: if full decompilation is  achieved this function can probably be deleted.
__attribute__((naked)) void InitUnknownWramStructureCall()
{
    InitUnknownWramStructure((uint8_t)0x3006560, (uint32_t)0x3006570, 0x10);
}
