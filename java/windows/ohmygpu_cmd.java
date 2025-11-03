import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class ohmygpu_cmd {
    
    static class GPUData {
        String name;
        String totalMemory;
        String usedMemory;
        String utilization;
        
        GPUData(String name, String totalMemory, String usedMemory, String utilization) {
            this.name = name;
            this.totalMemory = totalMemory;
            this.usedMemory = usedMemory;
            this.utilization = utilization;
        }
    }
    
    public static GPUData getGpuInfo() {
        String os = System.getProperty("os.name").toLowerCase();
        
        if (os.contains("win")) {
            return getGpuInfoWindows();
        } else if (os.contains("linux")) {
            return getGpuInfoLinux();
        } else if (os.contains("mac")) {
            return getGpuInfoMacos();
        }
        
        return null;
    }
    
    private static GPUData getGpuInfoWindows() {
        try {
            String[] cmd = {"nvidia-smi", "--query-gpu=name,memory.total,memory.used,utilization.gpu", "--format=csv,noheader"};
            String output = executeCommand(cmd);
            if (output != null && !output.isEmpty()) {
                String[] parts = output.trim().split(",");
                if (parts.length >= 4) {
                    return new GPUData(
                        parts[0].trim(),
                        parts[1].trim(),
                        parts[2].trim(),
                        parts[3].trim()
                    );
                }
            }
        } catch (Exception e) {
        }
        
        try {
            String[] cmd = {"rocm-smi", "--showid", "--showtemp"};
            String output = executeCommand(cmd);
            if (output != null && output.contains("GPU")) {
                return new GPUData("AMD Radeon GPU", "N/A", "N/A", "N/A");
            }
        } catch (Exception e) {
        }
        
        try {
            String[] cmd = {"wmic", "path", "win32_videocontroller", "get", "name,adapterram"};
            String output = executeCommand(cmd);
            if (output != null && !output.isEmpty()) {
                String[] lines = output.trim().split("\n");
                if (lines.length > 1) {
                    for (int i = 1; i < lines.length; i++) {
                        String line = lines[i].trim();
                        if (!line.isEmpty()) {
                            String[] parts = line.split("\\s{2,}");
                            if (parts.length >= 2) {
                                String name = parts[0].trim();
                                String mem = parts[parts.length - 1].trim();
                                
                                if (!name.isEmpty() && !name.toLowerCase().contains("name")) {
                                    try {
                                        long memBytes = Long.parseLong(mem);
                                        if (memBytes > 0) {
                                            return new GPUData(name, formatMemory(memBytes), "N/A", "N/A");
                                        }
                                    } catch (NumberFormatException e) {
                                        return new GPUData(name, "N/A", "N/A", "N/A");
                                    }
                                }
                            }
                        }
                    }
                }
            }
        } catch (Exception e) {
        }
        
        try {
            String[] cmd = {"powershell", "-Command", "Get-WmiObject Win32_VideoController | Select-Object Name, AdapterRAM"};
            String output = executeCommand(cmd);
            if (output != null && !output.isEmpty()) {
                String[] lines = output.trim().split("\n");
                for (int i = 1; i < lines.length; i++) {
                    String line = lines[i].trim();
                    if (!line.isEmpty() && !line.contains("---")) {
                        String[] parts = line.split("\\s{2,}");
                        if (parts.length >= 1) {
                            String name = parts[0].trim();
                            if (!name.isEmpty() && !name.toLowerCase().contains("name")) {
                                try {
                                    if (parts.length >= 2) {
                                        long memBytes = Long.parseLong(parts[parts.length - 1].trim());
                                        if (memBytes > 0) {
                                            return new GPUData(name, formatMemory(memBytes), "N/A", "N/A");
                                        }
                                    }
                                } catch (NumberFormatException e) {
                                    return new GPUData(name, "N/A", "N/A", "N/A");
                                }
                            }
                        }
                    }
                }
            }
        } catch (Exception e) {
        }
        
        return null;
    }
    
    private static GPUData getGpuInfoLinux() {
        try {
            String[] cmd = {"nvidia-smi", "--query-gpu=name,memory.total,memory.used,utilization.gpu", "--format=csv,noheader"};
            String output = executeCommand(cmd);
            if (output != null && !output.isEmpty()) {
                String[] parts = output.trim().split(",");
                if (parts.length >= 4) {
                    return new GPUData(
                        parts[0].trim(),
                        parts[1].trim(),
                        parts[2].trim(),
                        parts[3].trim()
                    );
                }
            }
        } catch (Exception e) {
        }
        

        try {
            String[] cmd = {"rocm-smi", "--showid"};
            String output = executeCommand(cmd);
            if (output != null && output.contains("GPU")) {
                return new GPUData("AMD Radeon GPU", "N/A", "N/A", "N/A");
            }
        } catch (Exception e) {
        }

        try {
            String[] cmd = {"lspci", "-v"};
            String output = executeCommand(cmd);
            if (output != null && !output.isEmpty()) {
                String[] lines = output.split("\n");
                for (String line : lines) {
                    if ((line.contains("VGA compatible controller") || 
                         line.contains("Display controller") || 
                         line.contains("3D controller")) &&
                        (line.contains("Intel") || line.contains("AMD") || line.contains("NVIDIA") || 
                         line.contains("Radeon") || line.contains("RTX") || line.contains("GTX") || 
                         line.contains("Arc"))) {
                        String gpuName = line.contains(": ") ? line.split(": ", 2)[1] : line;
                        return new GPUData(gpuName.trim(), "N/A", "N/A", "N/A");
                    }
                }
            }
        } catch (Exception e) {
        }
        
        return null;
    }
    
    private static GPUData getGpuInfoMacos() {
        try {
            String[] cmd = {"system_profiler", "SPDisplaysDataType"};
            String output = executeCommand(cmd);
            if (output != null && !output.isEmpty()) {
                Map<String, String> gpuInfo = new HashMap<>();
                String[] lines = output.split("\n");
                
                for (String line : lines) {
                    if (line.contains("Chipset Model")) {
                        String name = line.contains(": ") ? line.split(": ", 2)[1] : "";
                        gpuInfo.put("name", name.trim());
                    }
                    if (line.contains("VRAM")) {
                        String vramStr = line.contains(": ") ? line.split(": ", 2)[1] : "";
                        Pattern pattern = Pattern.compile("(\\d+)\\s*([MG])");
                        Matcher matcher = pattern.matcher(vramStr);
                        if (matcher.find()) {
                            long size = Long.parseLong(matcher.group(1));
                            String unit = matcher.group(2);
                            long bytesVal = size * ("G".equals(unit) ? 1024*1024*1024 : 1024*1024);
                            gpuInfo.put("total_memory", formatMemory(bytesVal));
                        }
                    }
                }
                
                if (!gpuInfo.isEmpty()) {
                    return new GPUData(
                        gpuInfo.getOrDefault("name", "Unknown"),
                        gpuInfo.getOrDefault("total_memory", "N/A"),
                        "N/A",
                        "N/A"
                    );
                }
            }
        } catch (Exception e) {
        }
        
        return null;
    }
    
    private static String formatMemory(long bytesValue) {
        String[] units = {"B", "KB", "MB", "GB", "TB"};
        double size = bytesValue;
        int unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return String.format("%.1f %s", size, units[unitIndex]);
    }
    
    private static String executeCommand(String[] cmd) throws Exception {
        try {
            ProcessBuilder pb = new ProcessBuilder(cmd);
            pb.redirectErrorStream(true);
            Process process = pb.start();
            
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
            
            process.waitFor();
            reader.close();
            
            return output.length() > 0 ? output.toString() : null;
        } catch (Exception e) {
            return null;
        }
    }
    
    public static void printGpuInfo() {
        System.out.println("\nOH MY GPU:\n");
        
        GPUData gpuInfo = getGpuInfo();
        
        if (gpuInfo != null) {
            System.out.println("GPU model:      " + gpuInfo.name);
            System.out.println("Total memory:   " + gpuInfo.totalMemory);
            System.out.println("Used memory:    " + gpuInfo.usedMemory);
            System.out.println("Utilization:    " + gpuInfo.utilization);
            System.out.println("\nGPU is fine.");
        } else {
            System.out.println("[ERROR] GPU not found!");
            System.out.println("[ERROR] Make sure GPU drivers are installed.");
        }
    }
    
    public static void main(String[] args) {
        printGpuInfo();
    }
}