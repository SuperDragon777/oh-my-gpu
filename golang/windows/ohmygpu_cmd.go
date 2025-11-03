package main

import (
	"fmt"
	"os/exec"
	"strings"
)

func getGPUInfo() map[string]string {
	gpuInfo := getNvidiaGPUInfo()
	if gpuInfo != nil {
		return gpuInfo
	}

	gpuInfo = getAmdGPUInfo()
	if gpuInfo != nil {
		return gpuInfo
	}

	gpuInfo = getIntegratedGPUInfo()
	if gpuInfo != nil {
		return gpuInfo
	}

	return nil
}

func getNvidiaGPUInfo() map[string]string {
	cmd := exec.Command("nvidia-smi", "--query-gpu=name,memory.total,memory.used,utilization.gpu", "--format=csv,noheader")
	output, err := cmd.CombinedOutput()
	if err != nil {
		return nil
	}

	info := strings.Split(string(output), ",")
	if len(info) < 4 {
		return nil
	}

	return map[string]string{
		"name":         strings.TrimSpace(info[0]),
		"total_memory": strings.TrimSpace(info[1]),
		"used_memory":  strings.TrimSpace(info[2]),
		"utilization":  strings.TrimSpace(info[3]),
	}
}

func getAmdGPUInfo() map[string]string {
	cmd := exec.Command("rocm-smi", "--showid", "--showtemp")
	output, err := cmd.CombinedOutput()
	if err != nil {
		return nil
	}

	if strings.Contains(string(output), "GPU") {
		return map[string]string{
			"name":         "AMD Radeon GPU",
			"total_memory": "N/A",
			"used_memory":  "N/A",
			"utilization":  "N/A",
		}
	}
	return nil
}

func getIntegratedGPUInfo() map[string]string {
	cmd := exec.Command("wmic", "path", "win32_videocontroller", "get", "name")
	output, err := cmd.CombinedOutput()
	if err != nil {
		return nil
	}

	if strings.Contains(string(output), "Intel") {
		return map[string]string{
			"name":         "Intel Integrated GPU",
			"total_memory": "N/A",
			"used_memory":  "N/A",
			"utilization":  "N/A",
		}
	}
	return nil
}

func printGPUInfo() {
	gpuInfo := getGPUInfo()
	if gpuInfo != nil {
		fmt.Println("\nOH MY GPU:\n")
		fmt.Printf("GPU model:      %s\n", gpuInfo["name"])
		fmt.Printf("Total memory:   %s\n", gpuInfo["total_memory"])
		fmt.Printf("Used memory:    %s\n", gpuInfo["used_memory"])
		fmt.Printf("Utilization:    %s\n", gpuInfo["utilization"])
		fmt.Println("\nGPU is fine.")
	} else {
		fmt.Println("[ERROR] GPU not found!")
		fmt.Println("[ERROR] Make sure GPU drivers are installed.")
	}
}

func main() {
	printGPUInfo()
}
