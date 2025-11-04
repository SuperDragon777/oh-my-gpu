import subprocess
import re


def get_processor_name():
    for prop in ('ro.chipname', 'ro.hardware'):
        try:
            result = subprocess.run(
                ['getprop', prop],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )
            if result.returncode == 0 and (processor := result.stdout.strip()):
                return processor
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    
    try:
        with open('/proc/cpuinfo', 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'Hardware' in line or 'Processor' in line:
                    if ':' in line:
                        return line.split(':', 1)[1].strip()
    except (FileNotFoundError, OSError, IOError):
        pass
    
    return "Unknown Processor"


def get_memory_info():
    mem_data = {}
    
    try:
        with open('/proc/meminfo', 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                key, _, value = line.partition(':')
                if key in ('MemTotal', 'MemAvailable'):
                    # Извлечь числовое значение и преобразовать в МБ
                    match = re.search(r'(\d+)', value)
                    if match:
                        mem_data[key] = int(match.group(1)) // 1024
    except (FileNotFoundError, OSError, IOError):
        return {'total': 'N/A', 'used': 'N/A'}
    
    if 'MemTotal' in mem_data and 'MemAvailable' in mem_data:
        mem_used = mem_data['MemTotal'] - mem_data['MemAvailable']
        return {
            'total': f"{mem_data['MemTotal']} MB",
            'used': f"{mem_used} MB"
        }
    
    return {'total': 'N/A', 'used': 'N/A'}


def print_gpu_info():
    processor = get_processor_name()
    memory = get_memory_info()
    
    print("\nOH MY GPU:\n")
    print(f"Processor:      {processor}")
    print(f"Total memory:   {memory['total']}")
    print(f"Used memory:    {memory['used']}")
    print(f"Utilization:    N/A")
    print("\nGPU is fine.")


if __name__ == "__main__":
    print_gpu_info()