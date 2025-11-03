#include <windows.h>
#include <stdio.h>
#include <stdlib.h>

void get_gpu_info(char *output, size_t size) {
    FILE *fp;
    char buffer[1024];

    fp = _popen("nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader", "r");
    if (fp) {
        if (fgets(buffer, sizeof(buffer), fp) != NULL) {
            snprintf(output, size, "GPU model: %s", buffer);
            _pclose(fp);
            return;
        }
        _pclose(fp);
    }

    fp = _popen("wmic path win32_VideoController get Name,AdapterRAM", "r");
    if (fp) {
        int first_line = 1;
        while (fgets(buffer, sizeof(buffer), fp)) {
            if (first_line) { first_line = 0; continue; }
            if (strlen(buffer) > 2) {
                snprintf(output, size, "GPU info:\n%s", buffer);
                _pclose(fp);
                return;
            }
        }
        _pclose(fp);
    }

    snprintf(output, size, "GPU not found!\nMake sure GPU drivers are installed.");
}

int main() {
    char gpu_info[1024] = {0};

    get_gpu_info(gpu_info, sizeof(gpu_info));

    MessageBoxA(NULL, gpu_info, "OH MY GPU", MB_OK | MB_ICONINFORMATION);

    return 0;
}
