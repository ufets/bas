package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"strings"
	"syscall"
	"time"
	"unsafe"
)

var (
	lastMouseX, lastMouseY int32
)

type point struct {
	x int32
	y int32
}

// GetCursorPos retrieves the cursor's position
func GetCursorPos(pt *point) bool {
	mod := syscall.NewLazyDLL("user32.dll").NewProc("GetCursorPos")
	r, _, _ := mod.Call(uintptr(unsafe.Pointer(pt)))
	return r != 0
}

// checkMouseMovement checks if the mouse position has changed after 10 seconds
func checkMouseMovement() bool {
	var initialPos, currentPos point
	GetCursorPos(&initialPos)

	fmt.Println("Waiting 10 seconds to check mouse movement...")
	time.Sleep(10 * time.Second)

	GetCursorPos(&currentPos)

	return initialPos.x != currentPos.x || initialPos.y != currentPos.y
}

// checkDesktopFiles checks if there are files on the desktop
func checkDesktopFiles() bool {
	desktopPath := os.Getenv("USERPROFILE") + "\\Desktop"
	files, err := ioutil.ReadDir(desktopPath)
	if err != nil {
		return false
	}
	return len(files) > 0
}

// checkBrowserHistory checks if browser history files exist (example for Chrome)
func checkBrowserHistory() bool {
	historyPath := os.Getenv("USERPROFILE") + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History"
	if _, err := os.Stat(historyPath); os.IsNotExist(err) {
		return false
	}
	return true
}

// checkRunningProcesses checks for user-related processes
func checkRunningProcesses() bool {
	processesToCheck := []string{"chrome.exe", "firefox.exe", "explorer.exe", "notepad.exe"}
	cmd := exec.Command("tasklist")
	output, err := cmd.Output()
	if err != nil {
		return false
	}

	outputStr := string(output)
	for _, process := range processesToCheck {
		if strings.Contains(outputStr, process) {
			return true
		}
	}
	return false
}

// checkVirtualMachineArtifacts checks for VM-related indicators
func checkVirtualMachineArtifacts() bool {
	cmd := exec.Command("cmd", "/C", "wmic bios get smbiosbiosversion")
	output, err := cmd.Output()
	if err != nil {
		return false
	}

	outputStr := strings.ToLower(string(output))
	if strings.Contains(outputStr, "vmware") || strings.Contains(outputStr, "virtualbox") || strings.Contains(outputStr, "qemu") {
		return true
	}
	return false
}

// delayExecutionIfNoActivity checks all indicators and delays if no activity is found
func delayExecutionIfNoActivity() {
	fmt.Println("Checking user activity...")

	mouseMoved := checkMouseMovement()
	desktopFiles := checkDesktopFiles()
	browserHistory := checkBrowserHistory()
	processesRunning := checkRunningProcesses()
	isVirtualMachine := checkVirtualMachineArtifacts()

	if mouseMoved {
		fmt.Println("Mouse movement detected.")
	} else {
		fmt.Println("No mouse movement detected.")
	}

	if desktopFiles {
		fmt.Println("Files detected on desktop.")
	} else {
		fmt.Println("No files on desktop.")
	}

	if browserHistory {
		fmt.Println("Browser history detected.")
	} else {
		fmt.Println("No browser history detected.")
	}

	if processesRunning {
		fmt.Println("Active user processes detected.")
	} else {
		fmt.Println("No active user processes detected.")
	}

	if isVirtualMachine {
		fmt.Println("This system is running in a virtual machine.")
	} else {
		fmt.Println("This system is not running in a virtual machine.")
	}

	if !mouseMoved && !desktopFiles && !browserHistory && !processesRunning && !isVirtualMachine {
		fmt.Println("No user activity detected. Exiting program.")
		time.Sleep(2 * time.Second)
		os.Exit(0)
	}

	fmt.Println("User activity confirmed. Continuing execution...")
}

func main() {
	fmt.Println("Program started...")

	// Check user activity and VM status before execution
	delayExecutionIfNoActivity()

	// Main program logic
	fmt.Println("Main program logic executing...")
}
