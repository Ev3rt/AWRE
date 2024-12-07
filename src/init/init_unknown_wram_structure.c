#include <gba_types.h>

// TODO: determine what kind of structure is initialized here.
void InitUnknownWramStructure(uint8_t *param_1, uint32_t *param_2, int count)
{
    param_1[0] = 0;
    param_1[1] = (uint8_t)count;
    param_1[2] = 0;
    *(uint32_t *)(param_1 + 4) = 0;
    *(uint32_t **)(param_1 + 8) = param_2;
    *(uint32_t **)(param_1 + 12) = param_2;

    if (count > 0)
    {
        do
        {
            *param_2 = 0;
            param_2 += 3;
            count--;
        } while (count > 0);
    }
}
