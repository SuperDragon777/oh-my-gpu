#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void format_memory(long bytes, char *output, size_t size) {
    if (bytes < 1024) {
        snprintf(output, size, "%ld B", bytes);
    } else if (bytes < 1024 * 1024) {
        snprintf(output, size, "%.1f KB", bytes / 1024.0);
    } else if (bytes < 1024 * 1024 * 1024) {
        snprintf(output, size, "%.1f MB", bytes / (1024.0 * 1024));
    } else {
        snprintf(output, size, "%.1f GB", bytes / (1024.0 * 1024 * 1024));
    }
}

void get_gpu_info() {
    FILE *fp;
    char buffer[1024];

    fp = _popen("nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader", "r");
    if (fp) {
        if (fgets(buffer, sizeof(buffer), fp) != NULL) {
            char name[128], total_mem[64], used_mem[64], utilization[64];
            if (sscanf(buffer, "%127[^,], %63[^,], %63[^,], %63[^\n]", name, total_mem, used_mem, utilization) == 4) {
                printf("GPU model:      %s\n", name);
                printf("Total memory:   %s\n", total_mem);
                printf("Used memory:    %s\n", used_mem);
                printf("Utilization:    %s\n", utilization);
                _pclose(fp);
                return;
            }
        }
        _pclose(fp);
    }

    fp = _popen("wmic path win32_VideoController get Name,AdapterRAM", "r");
    if (fp) {
        int first_line = 1;
        while (fgets(buffer, sizeof(buffer), fp)) {
            if (first_line) {
                first_line = 0;
                continue;
            }
            if (strlen(buffer) > 2) {
                char name[128];
                long mem = 0;
                if (sscanf(buffer, "%127[^\r\n0123456789]%ld", name, &mem) >= 1) {
                    char mem_str[64];
                    if (mem > 0) {
                        format_memory(mem, mem_str, sizeof(mem_str));
                    } else {
                        snprintf(mem_str, sizeof(mem_str), "N/A");
                    }
                    printf("GPU model:      %s\n", name);
                    printf("Total memory:   %s\n", mem_str);
                    printf("Used memory:    N/A\n");
                    printf("Utilization:    N/A\n");
                    _pclose(fp);
                    return;
                }
            }
        }
        _pclose(fp);
    }

    printf("[ERROR] GPU not found!\n");
    printf("[ERROR] Make sure GPU drivers are installed.\n");
}

int main() {
    printf("\nOH MY GPU:\n\n");

    get_gpu_info();

    printf("\nPress Enter, for exit...");
    getchar();

    return 0;
}
