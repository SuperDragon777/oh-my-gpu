<?php

function get_gpu_info() {
    $system = PHP_OS_FAMILY;

    if ($system === "Windows") {
        return get_gpu_info_windows();
    } elseif ($system === "Linux") {
        return get_gpu_info_linux();
    } elseif ($system === "Darwin") {
        return get_gpu_info_macos();
    }

    return null;
}

function get_gpu_info_windows() {
    $output = [];
    $return_var = 0;
    exec('nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader', $output, $return_var);
    if ($return_var === 0 && count($output) > 0) {
        $info = array_map('trim', explode(',', $output[0]));
        return [
            'name' => $info[0],
            'total_memory' => $info[1],
            'used_memory' => $info[2],
            'utilization' => $info[3],
        ];
    }

    exec('rocm-smi --showid --showtemp', $output, $return_var);
    if ($return_var === 0 && implode("\n", $output) !== '') {
        return [
            'name' => 'AMD Radeon GPU',
            'total_memory' => 'N/A',
            'used_memory' => 'N/A',
            'utilization' => 'N/A',
        ];
    }

    exec('wmic path win32_videocontroller get name,adapterram', $output, $return_var);
    if ($return_var === 0 && count($output) > 1) {
        for ($i = 1; $i < count($output); $i++) {
            $line = trim($output[$i]);
            if ($line !== '') {
                $parts = preg_split('/\s{2,}/', $line);
                if (count($parts) >= 2) {
                    $name = $parts[0];
                    $mem = is_numeric($parts[1]) ? format_memory((int)$parts[1]) : 'N/A';
                    return [
                        'name' => $name,
                        'total_memory' => $mem,
                        'used_memory' => 'N/A',
                        'utilization' => 'N/A',
                    ];
                }
            }
        }
    }

    return null;
}

function get_gpu_info_linux() {
    $output = [];
    $return_var = 0;
    exec('nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader', $output, $return_var);
    if ($return_var === 0 && count($output) > 0) {
        $info = array_map('trim', explode(',', $output[0]));
        return [
            'name' => $info[0],
            'total_memory' => $info[1],
            'used_memory' => $info[2],
            'utilization' => $info[3],
        ];
    }

    exec('rocm-smi --showid', $output, $return_var);
    if ($return_var === 0 && implode("\n", $output) !== '') {
        return [
            'name' => 'AMD Radeon GPU',
            'total_memory' => 'N/A',
            'used_memory' => 'N/A',
            'utilization' => 'N/A',
        ];
    }

    exec('lspci -v', $output, $return_var);
    if ($return_var === 0) {
        foreach ($output as $line) {
            if (preg_match('/(VGA compatible controller|Display controller|3D controller)/i', $line) &&
                preg_match('/(Intel|AMD|NVIDIA|Radeon|RTX|GTX|Arc)/i', $line)) {
                $parts = explode(': ', $line, 2);
                $gpu_name = count($parts) > 1 ? $parts[1] : $line;
                return [
                    'name' => trim($gpu_name),
                    'total_memory' => 'N/A',
                    'used_memory' => 'N/A',
                    'utilization' => 'N/A',
                ];
            }
        }
    }

    return null;
}

function get_gpu_info_macos() {
    $output = [];
    $return_var = 0;
    exec('system_profiler SPDisplaysDataType', $output, $return_var);
    if ($return_var === 0 && count($output) > 0) {
        $gpu_info = [];
        foreach ($output as $line) {
            if (strpos($line, 'Chipset Model') !== false) {
                $gpu_info['name'] = trim(explode(':', $line, 2)[1]);
            }
            if (strpos($line, 'VRAM') !== false) {
                $vram_str = trim(explode(':', $line, 2)[1]);
                if (preg_match('/(\d+)\s*([MG])/i', $vram_str, $matches)) {
                    $size = (int)$matches[1];
                    $unit = strtoupper($matches[2]);
                    $bytes_val = $size * ($unit === 'G' ? 1024**3 : 1024**2);
                    $gpu_info['total_memory'] = format_memory($bytes_val);
                }
            }
        }
        if (!empty($gpu_info)) {
            if (!isset($gpu_info['total_memory'])) $gpu_info['total_memory'] = 'N/A';
            $gpu_info['used_memory'] = 'N/A';
            $gpu_info['utilization'] = 'N/A';
            return $gpu_info;
        }
    }
    return null;
}

function format_memory($bytes) {
    $units = ['B', 'KB', 'MB', 'GB'];
    foreach ($units as $unit) {
        if ($bytes < 1024) return round($bytes, 1) . ' ' . $unit;
        $bytes /= 1024;
    }
    return round($bytes, 1) . ' TB';
}

function print_gpu_info() {
    echo "\nOH MY GPU:\n\n";

    $gpu_info = get_gpu_info();

    if ($gpu_info) {
        echo "GPU model:      {$gpu_info['name']}\n";
        echo "Total memory:   {$gpu_info['total_memory']}\n";
        echo "Used memory:    {$gpu_info['used_memory']}\n";
        echo "Utilization:    {$gpu_info['utilization']}\n";
        echo "\nGPU is fine.\n";
    } else {
        echo "[ERROR] GPU not found!\n";
        echo "[ERROR] Make sure GPU drivers are installed.\n";
    }
}

print_gpu_info();

?>
