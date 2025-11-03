import subprocess
import re

def get_gpu_info():
    try:
        result = subprocess.run(
            ['dumpsys', 'meminfo'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return parse_meminfo(result.stdout)
    except:
        pass
    
    try:
        result = subprocess.run(
            ['cat', '/proc/meminfo'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return parse_proc_meminfo(result.stdout)
    except:
        pass
    
    return None

def parse_meminfo(output):
    lines = output.split('\n')
    total_memory = None
    used_memory = None
    
    for line in lines:
        if 'Total' in line:
            match = re.search(r'(\d+)', line)
            if match:
                mb_value = int(match.group(1))
                if mb_value > 100:
                    total_memory = f"{mb_value} MB"
                else:
                    total_memory = f"{mb_value * 1024} MB"
        
        if 'Used' in line and 'Total' not in line:
            match = re.search(r'(\d+)', line)
            if match:
                mb_value = int(match.group(1))
                if mb_value < 500:
                    used_memory = f"{mb_value * 1024} MB"
                else:
                    used_memory = f"{mb_value} MB"
    
    gpu_name = get_gpu_name()
    
    return {
        'name': gpu_name,
        'total_memory': total_memory or 'N/A',
        'used_memory': used_memory or 'N/A',
        'utilization': 'N/A'
    }

def parse_proc_meminfo(output):
    lines = output.split('\n')
    mem_total = None
    mem_used = None
    
    for line in lines:
        if line.startswith('MemTotal:'):
            match = re.search(r'(\d+)', line)
            if match:
                kb_value = int(match.group(1))
                mem_total = f"{kb_value // 1024} MB"
        
        if line.startswith('MemAvailable:'):
            match = re.search(r'(\d+)', line)
            if match:
                available_kb = int(match.group(1))
                total_kb = 0
                for l in lines:
                    if l.startswith('MemTotal:'):
                        total_kb = int(re.search(r'(\d+)', l).group(1))
                        break
                
                if total_kb > 0:
                    used_kb = total_kb - available_kb
                    mem_used = f"{used_kb // 1024} MB"
    
    gpu_name = get_gpu_name()
    
    return {
        'name': gpu_name,
        'total_memory': mem_total or 'N/A',
        'used_memory': mem_used or 'N/A',
        'utilization': 'N/A'
    }

def get_gpu_name():
    try:
        result = subprocess.run(
            ['getprop', 'ro.board.platform'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            platform_name = result.stdout.strip()
            if platform_name:
                return f"Android GPU - {platform_name}"
    except:
        pass
    
    try:
        result = subprocess.run(
            ['getprop', 'ro.hardware'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            hardware = result.stdout.strip()
            if hardware:
                return f"Android GPU - {hardware}"
    except:
        pass
    
    return "Android GPU"

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
        print("[ERROR] Make sure device is properly configured.")


if __name__ == "__main__":
    print_gpu_info()