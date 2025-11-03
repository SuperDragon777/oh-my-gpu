import subprocess
import platform
import re

def get_gpu_info():
    system = platform.system()
    
    if system == "Windows":
        return get_gpu_info_windows()
    elif system == "Linux":
        return get_gpu_info_linux()
    elif system == "Darwin":
        return get_gpu_info_macos()
    
    return None

def get_gpu_info_windows():
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total,memory.used,utilization.gpu', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            info = result.stdout.strip().split(',')
            return {
                'name': info[0].strip(),
                'total_memory': info[1].strip(),
                'used_memory': info[2].strip(),
                'utilization': info[3].strip()
            }
    except:
        pass
    
    try:
        result = subprocess.run(
            ['rocm-smi', '--showid', '--showtemp'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and 'GPU' in result.stdout:
            return {
                'name': 'AMD Radeon GPU',
                'total_memory': 'N/A',
                'used_memory': 'N/A',
                'utilization': 'N/A'
            }
    except:
        pass
    
    try:
        result = subprocess.run(
            ['wmic', 'path', 'win32_videocontroller', 'get', 'name,adapterram'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for i in range(1, len(lines)):
                if lines[i].strip():
                    parts = lines[i].strip().rsplit(None, 1)
                    if len(parts) == 2:
                        name, mem = parts
                        return {
                            'name': name.strip(),
                            'total_memory': format_memory(int(mem)) if mem.isdigit() else 'N/A',
                            'used_memory': 'N/A',
                            'utilization': 'N/A'
                        }
    except:
        pass
    
    return None

def get_gpu_info_linux():
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total,memory.used,utilization.gpu', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            info = result.stdout.strip().split(',')
            return {
                'name': info[0].strip(),
                'total_memory': info[1].strip(),
                'used_memory': info[2].strip(),
                'utilization': info[3].strip()
            }
    except:
        pass
    
    try:
        result = subprocess.run(
            ['rocm-smi', '--showid'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and 'GPU' in result.stdout:
            return {
                'name': 'AMD Radeon GPU',
                'total_memory': 'N/A',
                'used_memory': 'N/A',
                'utilization': 'N/A'
            }
    except:
        pass
    
    try:
        result = subprocess.run(
            ['lspci', '-v'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if 'VGA compatible controller' in line or 'Display controller' in line or '3D controller' in line:
                    if any(x in line for x in ['Intel', 'AMD', 'NVIDIA', 'Radeon', 'RTX', 'GTX', 'Arc']):
                        gpu_name = line.split(': ', 1)[-1] if ': ' in line else line
                        return {
                            'name': gpu_name.strip(),
                            'total_memory': 'N/A',
                            'used_memory': 'N/A',
                            'utilization': 'N/A'
                        }
    except:
        pass
    
    return None

def get_gpu_info_macos():
    try:
        result = subprocess.run(
            ['system_profiler', 'SPDisplaysDataType'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            gpu_info = {}
            
            for line in lines:
                if 'Chipset Model' in line:
                    gpu_info['name'] = line.split(': ', 1)[-1].strip()
                if 'VRAM' in line:
                    vram_str = line.split(': ', 1)[-1].strip()
                    match = re.search(r'(\d+)\s*([MG])', vram_str)
                    if match:
                        size = int(match.group(1))
                        unit = match.group(2)
                        bytes_val = size * ({'M': 1024**2, 'G': 1024**3}.get(unit, 1))
                        gpu_info['total_memory'] = format_memory(bytes_val)
            
            if gpu_info:
                if 'total_memory' not in gpu_info:
                    gpu_info['total_memory'] = 'N/A'
                gpu_info['used_memory'] = 'N/A'
                gpu_info['utilization'] = 'N/A'
                return gpu_info
    except:
        pass
    
    return None

def format_memory(bytes_value):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.1f} TB"

def print_gpu_info():
    print("\nOH MY GPU:\n")
    
    gpu_info = get_gpu_info()
    
    if gpu_info:
        print(f"GPU model:      {gpu_info['name']}")
        print(f"Total memory:   {gpu_info['total_memory']}")
        print(f"Used memory:    {gpu_info['used_memory']}")
        print(f"Utilization:    {gpu_info['utilization']}")
        print("\nGPU is fine.")
    else:
        print("[ERROR] GPU not found!")
        print("[ERROR] Make sure GPU drivers are installed.")


if __name__ == "__main__":
    print_gpu_info()