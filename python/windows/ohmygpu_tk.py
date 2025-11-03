import tkinter as tk
from tkinter import ttk
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
            gpus = []
            for i in range(1, len(lines)):
                if lines[i].strip():
                    parts = lines[i].strip().rsplit(None, 1)
                    if len(parts) == 2:
                        name, mem = parts
                        gpus.append({
                            'name': name.strip(),
                            'total_memory': format_memory(int(mem)) if mem.isdigit() else 'N/A',
                            'used_memory': 'N/A',
                            'utilization': 'N/A'
                        })
            if gpus:
                return gpus[0]
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
            try:
                result2 = subprocess.run(
                    ['rocm-smi', '--showmeminfo', 'all'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result2.returncode == 0:
                    lines = result2.stdout.split('\n')
                    total_mem = 'N/A'
                    for line in lines:
                        if 'Total Memory' in line or 'Total' in line and 'Memory' in line:
                            match = re.search(r'(\d+)', line)
                            if match:
                                total_mem = format_memory(int(match.group(1)) * 1024 * 1024)
                                break
                    
                    return {
                        'name': 'AMD Radeon GPU',
                        'total_memory': total_mem,
                        'used_memory': 'N/A',
                        'utilization': 'N/A'
                    }
            except:
                pass
            
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
                        gpu_name = gpu_name.strip()
                        
                        mem = 'N/A'
                        for j in range(i+1, min(i+10, len(lines))):
                            if 'Memory at' in lines[j] or 'Region' in lines[j]:
                                match = re.search(r'(\d+)([KMG])', lines[j])
                                if match:
                                    size = int(match.group(1))
                                    unit = match.group(2)
                                    bytes_val = size * {'K': 1024, 'M': 1024**2, 'G': 1024**3}.get(unit, 1)
                                    mem = format_memory(bytes_val)
                                    break
                        
                        return {
                            'name': gpu_name,
                            'total_memory': mem,
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

def create_gpu_window():
    root = tk.Tk()
    root.title("oh-my-gpu")
    root.configure(bg='#2b2b2b')
    root.resizable(False, False)
    
    main_frame = tk.Frame(root, bg='#2b2b2b')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    title_label = tk.Label(
        main_frame,
        text='OH MY GPU',
        font=('Arial', 20, 'bold'),
        bg='#2b2b2b',
        fg='#00ff00'
    )
    title_label.pack(pady=10)
    
    separator = ttk.Separator(main_frame, orient='horizontal')
    separator.pack(fill=tk.X, pady=10)
    
    info_display_frame = tk.Frame(main_frame, bg='#2b2b2b')
    info_display_frame.pack(fill=tk.BOTH, expand=True)
    
    def update_display():
        for widget in info_display_frame.winfo_children():
            widget.destroy()
        
        gpu_info = get_gpu_info()
        
        if gpu_info:
            info_frame = tk.Frame(info_display_frame, bg='#1e1e1e', relief=tk.RAISED, bd=2)
            info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            name_label = tk.Label(
                info_frame,
                text='GPU model:',
                font=('Arial', 11, 'bold'),
                bg='#1e1e1e',
                fg='#ffffff',
                justify=tk.LEFT
            )
            name_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
            
            name_value = tk.Label(
                info_frame,
                text=gpu_info['name'],
                font=('Arial', 12),
                bg='#1e1e1e',
                fg='#00ff00'
            )
            name_value.pack(anchor=tk.W, padx=25, pady=(0, 10))
            
            sep2 = ttk.Separator(info_frame, orient='horizontal')
            sep2.pack(fill=tk.X, padx=15, pady=5)
            
            memory_label = tk.Label(
                info_frame,
                text='Total memory:',
                font=('Arial', 11, 'bold'),
                bg='#1e1e1e',
                fg='#ffffff'
            )
            memory_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
            
            memory_value = tk.Label(
                info_frame,
                text=gpu_info['total_memory'],
                font=('Arial', 12),
                bg='#1e1e1e',
                fg='#00ff00'
            )
            memory_value.pack(anchor=tk.W, padx=25, pady=(0, 10))
            
            sep3 = ttk.Separator(info_frame, orient='horizontal')
            sep3.pack(fill=tk.X, padx=15, pady=5)
            
            used_label = tk.Label(
                info_frame,
                text='Used memory:',
                font=('Arial', 11, 'bold'),
                bg='#1e1e1e',
                fg='#ffffff'
            )
            used_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
            
            used_value = tk.Label(
                info_frame,
                text=gpu_info['used_memory'],
                font=('Arial', 12),
                bg='#1e1e1e',
                fg='#00ff00'
            )
            used_value.pack(anchor=tk.W, padx=25, pady=(0, 10))
            
            sep4 = ttk.Separator(info_frame, orient='horizontal')
            sep4.pack(fill=tk.X, padx=15, pady=5)
            
            util_label = tk.Label(
                info_frame,
                text='Utilization:',
                font=('Arial', 11, 'bold'),
                bg='#1e1e1e',
                fg='#ffffff'
            )
            util_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
            
            util_value = tk.Label(
                info_frame,
                text=gpu_info['utilization'],
                font=('Arial', 12),
                bg='#1e1e1e',
                fg='#00ff00'
            )
            util_value.pack(anchor=tk.W, padx=25, pady=(0, 15))
            
            status_label = tk.Label(
                info_display_frame,
                text='GPU is fine',
                font=('Arial', 10),
                bg='#2b2b2b',
                fg='#00ff00'
            )
            status_label.pack(pady=10)
        else:
            error_frame = tk.Frame(info_display_frame, bg='#1e1e1e', relief=tk.RAISED, bd=2)
            error_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            error_label = tk.Label(
                error_frame,
                text='GPU not found!',
                font=('Arial', 12, 'bold'),
                bg='#1e1e1e',
                fg='#ff0000'
            )
            error_label.pack(pady=20)
            
            error_text = tk.Label(
                error_frame,
                text='Make sure that your GPU drivers are installed.',
                font=('Arial', 10),
                bg='#1e1e1e',
                fg='#ffffff',
                justify=tk.LEFT
            )
            error_text.pack(pady=10)
    
    button_frame = tk.Frame(main_frame, bg='#2b2b2b')
    button_frame.pack(pady=10)
    
    refresh_button = tk.Button(
        button_frame,
        text='RELOAD',
        command=update_display,
        font=('Arial', 10),
        bg='#404040',
        fg='#00ff00',
        padx=15,
        pady=8,
        relief=tk.RAISED,
        bd=1
    )
    refresh_button.pack(side=tk.LEFT, padx=5)
    
    exit_button = tk.Button(
        button_frame,
        text='CLOSE',
        command=root.quit,
        font=('Arial', 10),
        bg='#404040',
        fg='#ffffff',
        padx=15,
        pady=8,
        relief=tk.RAISED,
        bd=1
    )
    exit_button.pack(side=tk.LEFT, padx=5)
    
    update_display()
    
    root.mainloop()

if __name__ == "__main__":
    create_gpu_window()