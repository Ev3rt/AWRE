#include <gba_types.h>
#include <gba_interrupt.h>

#define DAT_INTERRUPT_MASK (*(volatile uint32_t *)0x3000710)

/*
Updates the Interrupt Enable and Interrupt Master Enable registers.
`mode` specifies how to combine the current and new values:
 - `0`: replace the current value with the new value.
 - `1`: AND the current and new values.
 - `2`: OR the current and new values.
 - Any other value for `mode` results in no change to the existing value.
`value` specifies the new value.
The final value is applied as follows:
    31 ........... 16 15 ............ 0
    00000000 0000000x yyyyyyyy yyyyyyyy
                    ^ ^^^^^^^^^^^^^^^^^
                  IME                IE
*/
void SetInterrupts(int mode, uint32_t value)
{
    switch (mode)
    {
    case 0: // Set
        DAT_INTERRUPT_MASK = value;
        break;

    case 1: // AND
        DAT_INTERRUPT_MASK &= value;
        break;

    case 2: // OR
        DAT_INTERRUPT_MASK |= value;
        break;

    default: // no-op
        break;
    }

    // Put the new mask into the IE register
    REG_IE = (uint16_t)DAT_INTERRUPT_MASK;

    // Update the Interrupt Master Enable based on the most significant bit of .
    REG_IME = (DAT_INTERRUPT_MASK & 0x10000) ? 1 : 0;
}
