/* SPDX-License-Identifier: Apache-2.0 */
#include "app.h"
#include "target.h"

int main(void)
{
    target_init();
    (void)app_main();
    for (;;) {
        /* app_main returns only when RTX5 startup fails. */
    }
}
