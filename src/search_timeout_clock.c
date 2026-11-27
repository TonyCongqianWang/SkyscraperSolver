#define _POSIX_C_SOURCE 200809L
#include "search_timeout.h"
#ifdef _WIN32
# include <windows.h>
double search_timeout_cpu_seconds(void)
{
    FILETIME creation, exit_time, kernel, user;
    ULARGE_INTEGER k, u;

    if (!GetProcessTimes(GetCurrentProcess(), &creation, &exit_time,
            &kernel, &user))
        return (-1.0);
    k.LowPart = kernel.dwLowDateTime;
    k.HighPart = kernel.dwHighDateTime;
    u.LowPart = user.dwLowDateTime;
    u.HighPart = user.dwHighDateTime;
    return ((double)k.QuadPart + (double)u.QuadPart) / 10000000.0;
}
#else
# include <time.h>
double search_timeout_cpu_seconds(void)
{
    struct timespec now;

    if (clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &now))
        return (-1.0);
    return ((double)now.tv_sec + (double)now.tv_nsec / 1e9);
}
#endif
