function Format-Memory($bytes) {
    $units = @('B', 'KB', 'MB', 'GB', 'TB')
    $i = 0
    while ($bytes -ge 1024 -and $i -lt $units.Length - 1) {
        $bytes = $bytes / 1024
        $i++
    }
    return "{0:N1} {1}" -f $bytes, $units[$i]
}

function Get-GPUInfoWindows {
    try {
        $nvidia = & nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader 2>$null
        if ($nvidia) {
            $info = $nvidia -split ','
            return @{
                Name = $info[0].Trim()
                TotalMemory = $info[1].Trim()
                UsedMemory = $info[2].Trim()
                Utilization = $info[3].Trim()
            }
        }
    } catch {}

    try {
        $amd = & rocm-smi --showid --showtemp 2>$null
        if ($amd -and $amd -match 'GPU') {
            return @{
                Name = "AMD Radeon GPU"
                TotalMemory = "N/A"
                UsedMemory = "N/A"
                Utilization = "N/A"
            }
        }
    } catch {}

    try {
        $gpus = Get-WmiObject Win32_VideoController
        foreach ($gpu in $gpus) {
            if ($gpu.Name) {
                $mem = if ($gpu.AdapterRAM) { Format-Memory $gpu.AdapterRAM } else { "N/A" }
                return @{
                    Name = $gpu.Name
                    TotalMemory = $mem
                    UsedMemory = "N/A"
                    Utilization = "N/A"
                }
            }
        }
    } catch {}

    return $null
}

function Print-GPUInfo {
    Write-Host "`nOH MY GPU:`n"

    $gpuInfo = Get-GPUInfoWindows

    if ($gpuInfo) {
        Write-Host "GPU model:      $($gpuInfo.Name)"
        Write-Host "Total memory:   $($gpuInfo.TotalMemory)"
        Write-Host "Used memory:    $($gpuInfo.UsedMemory)"
        Write-Host "Utilization:    $($gpuInfo.Utilization)"
        Write-Host "`nGPU is fine."
    } else {
        Write-Host "[ERROR] GPU not found!"
        Write-Host "[ERROR] Make sure GPU drivers are installed."
    }
}

Print-GPUInfo
