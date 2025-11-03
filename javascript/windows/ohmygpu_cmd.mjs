import { execSync } from "child_process";
import os from "os";

function getGPUInfo() {
  const platform = os.platform();

  if (platform === "win32") return getGPUInfoWindows();
  if (platform === "linux") return getGPUInfoLinux();
  if (platform === "darwin") return getGPUInfoMacOS();

  return null;
}

function getGPUInfoWindows() {
  // --- NVIDIA ---
  try {
    const result = execSync(
      "nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader",
      { encoding: "utf8", stdio: ["pipe", "pipe", "ignore"] }
    );
    if (result.trim()) {
      const info = result.trim().split(",");
      return {
        name: info[0].trim(),
        total_memory: info[1].trim(),
        used_memory: info[2].trim(),
        utilization: info[3].trim(),
      };
    }
  } catch {}

  // --- AMD ROCm ---
  try {
    const result = execSync("rocm-smi --showid --showtemp", {
      encoding: "utf8",
      stdio: ["pipe", "pipe", "ignore"],
    });
    if (result.includes("GPU")) {
      return {
        name: "AMD Radeon GPU",
        total_memory: "N/A",
        used_memory: "N/A",
        utilization: "N/A",
      };
    }
  } catch {}

  // --- Generic WMI ---
  try {
    const result = execSync(
      "wmic path win32_videocontroller get name,adapterram",
      { encoding: "utf8", stdio: ["pipe", "pipe", "ignore"] }
    );
    const lines = result.trim().split("\n");
    for (let i = 1; i < lines.length; i++) {
      if (lines[i].trim()) {
        const parts = lines[i].trim().split(/\s+(?=\d+$)/);
        if (parts.length === 2) {
          const [name, mem] = parts;
          return {
            name: name.trim(),
            total_memory: /^\d+$/.test(mem)
              ? formatMemory(parseInt(mem))
              : "N/A",
            used_memory: "N/A",
            utilization: "N/A",
          };
        }
      }
    }
  } catch {}

  return null;
}

function getGPUInfoLinux() {
  // --- NVIDIA ---
  try {
    const result = execSync(
      "nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader",
      { encoding: "utf8", stdio: ["pipe", "pipe", "ignore"] }
    );
    if (result.trim()) {
      const info = result.trim().split(",");
      return {
        name: info[0].trim(),
        total_memory: info[1].trim(),
        used_memory: info[2].trim(),
        utilization: info[3].trim(),
      };
    }
  } catch {}

  // --- AMD ROCm ---
  try {
    const result = execSync("rocm-smi --showid", {
      encoding: "utf8",
      stdio: ["pipe", "pipe", "ignore"],
    });
    if (result.includes("GPU")) {
      return {
        name: "AMD Radeon GPU",
        total_memory: "N/A",
        used_memory: "N/A",
        utilization: "N/A",
      };
    }
  } catch {}

  // --- lspci fallback ---
  try {
    const result = execSync("lspci -v", {
      encoding: "utf8",
      stdio: ["pipe", "pipe", "ignore"],
    });
    const lines = result.split("\n");
    for (const line of lines) {
      if (
        /(VGA compatible controller|Display controller|3D controller)/i.test(line)
      ) {
        if (/(Intel|AMD|NVIDIA|Radeon|RTX|GTX|Arc)/i.test(line)) {
          const gpuName = line.includes(": ") ? line.split(": ")[1] : line;
          return {
            name: gpuName.trim(),
            total_memory: "N/A",
            used_memory: "N/A",
            utilization: "N/A",
          };
        }
      }
    }
  } catch {}

  return null;
}

function getGPUInfoMacOS() {
  try {
    const result = execSync("system_profiler SPDisplaysDataType", {
      encoding: "utf8",
      stdio: ["pipe", "pipe", "ignore"],
    });
    const lines = result.split("\n");
    const gpuInfo = {};

    for (const line of lines) {
      if (line.includes("Chipset Model")) {
        gpuInfo.name = line.split(":")[1].trim();
      }
      if (line.includes("VRAM")) {
        const vramStr = line.split(":")[1].trim();
        const match = vramStr.match(/(\d+)\s*([MG])/);
        if (match) {
          const size = parseInt(match[1]);
          const unit = match[2];
          const bytesVal =
            size *
            (unit === "M" ? 1024 ** 2 : unit === "G" ? 1024 ** 3 : 1);
          gpuInfo.total_memory = formatMemory(bytesVal);
        }
      }
    }

    if (Object.keys(gpuInfo).length) {
      if (!gpuInfo.total_memory) gpuInfo.total_memory = "N/A";
      gpuInfo.used_memory = "N/A";
      gpuInfo.utilization = "N/A";
      return gpuInfo;
    }
  } catch {}

  return null;
}

function formatMemory(bytesValue) {
  const units = ["B", "KB", "MB", "GB"];
  let value = bytesValue;
  for (const unit of units) {
    if (value < 1024) {
      return `${value.toFixed(1)} ${unit}`;
    }
    value /= 1024;
  }
  return `${value.toFixed(1)} TB`;
}

function printGPUInfo() {
  console.log("\nOH MY GPU:\n");
  const gpuInfo = getGPUInfo();

  if (gpuInfo) {
    console.log(`GPU model:      ${gpuInfo.name}`);
    console.log(`Total memory:   ${gpuInfo.total_memory}`);
    console.log(`Used memory:    ${gpuInfo.used_memory}`);
    console.log(`Utilization:    ${gpuInfo.utilization}`);
    console.log("\nGPU is fine.");
  } else {
    console.log("[ERROR] GPU not found!");
    console.log("[ERROR] Make sure GPU drivers are installed.");
  }
}

printGPUInfo();
