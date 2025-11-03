local function format_memory(bytes_value)
    local units = {"B", "KB", "MB", "GB", "TB"}
    local i = 1
    while bytes_value >= 1024 and i < #units do
        bytes_value = bytes_value / 1024
        i = i + 1
    end
    return string.format("%.1f %s", bytes_value, units[i])
end

local function run_command(cmd)
    local handle = io.popen(cmd)
    if handle then
        local result = handle:read("*a")
        handle:close()
        return result
    end
    return nil
end

local function get_os_name()
    if jit and jit.os then
        return jit.os
    end

    local sep = package.config:sub(1,1)
    if sep == "\\" then
        return "Windows"
    else
        local f = io.popen("uname -s")
        if f then
            local os = f:read("*l")
            f:close()
            return os
        end
    end
    return "Unknown"
end

local function get_gpu_info_windows()
    local nvidia = run_command('nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader')
    if nvidia and nvidia ~= "" then
        local name, total, used, util = nvidia:match("([^,]+),%s*([^,]+),%s*([^,]+),%s*([^,]+)")
        return {
            name = name,
            total_memory = total,
            used_memory = used,
            utilization = util
        }
    end

    local amd = run_command('rocm-smi --showid --showtemp')
    if amd and amd:find("GPU") then
        return {
            name = "AMD Radeon GPU",
            total_memory = "N/A",
            used_memory = "N/A",
            utilization = "N/A"
        }
    end

    local wmic = run_command('wmic path win32_videocontroller get name,adapterram')
    if wmic then
        for line in wmic:gmatch("[^\r\n]+") do
            local name, mem = line:match("^(.-)%s+(%d+)$")
            if name and mem then
                return {
                    name = name,
                    total_memory = format_memory(tonumber(mem)),
                    used_memory = "N/A",
                    utilization = "N/A"
                }
            end
        end
    end

    return nil
end

local function get_gpu_info()
    local os_name = get_os_name()
    if os_name == "Windows" then
        return get_gpu_info_windows()
    else
        return nil
    end
end

local function print_gpu_info()
    print("\nOH MY GPU:\n")
    local gpu_info = get_gpu_info()
    if gpu_info then
        print(string.format("GPU model:      %s", gpu_info.name))
        print(string.format("Total memory:   %s", gpu_info.total_memory))
        print(string.format("Used memory:    %s", gpu_info.used_memory))
        print(string.format("Utilization:    %s", gpu_info.utilization))
        print("\nGPU is fine.")
    else
        print("[ERROR] GPU not found!")
        print("[ERROR] Make sure GPU drivers are installed.")
    end
end

print_gpu_info()
