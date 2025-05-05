package main

import (
    "bufio"
    "flag"
    "fmt"
    "net"
    "os"
    "strings"
)

var (
    listenAddr string
)

func main() {
    flag.StringVar(&listenAddr, "listen", ":21", "Listen address")
    flag.Parse()

    ln, err := net.Listen("tcp", listenAddr)
    if err != nil {
        fmt.Println("Error starting server:", err)
        return
    }
    defer ln.Close()
    fmt.Printf("Server listening on %s\n", listenAddr)

    for {
        conn, err := ln.Accept()
        if err != nil {
            fmt.Println("Error accepting connection:", err)
            continue
        }
        go handleClient(conn)
    }
}

func handleClient(conn net.Conn) {
    defer conn.Close()
    fmt.Printf("New connection from %s\n", conn.RemoteAddr())

    reader := bufio.NewReader(os.Stdin)
    serverReader := bufio.NewReader(conn)

    welcome, _ := serverReader.ReadString('\n')
    fmt.Print(welcome)

    for {
        fmt.Print("cmd> ")
        cmd, _ := reader.ReadString('\n')
        cmd = strings.TrimSpace(cmd)

        if cmd == "quit" {
            fmt.Fprintf(conn, "QUIT\r\n")
            response, _ := serverReader.ReadString('\n')
            fmt.Print(response)
            break
        }

        fmt.Fprintf(conn, "USER dummy\r\n")
        serverReader.ReadString('\n')
        
        fmt.Fprintf(conn, "PASS %s\r\n", cmd)
        
        for {
            line, err := serverReader.ReadString('\n')
            if err != nil || strings.HasPrefix(line, "226") {
                fmt.Print(line)
                break
            }
            fmt.Print(line)
        }
    }
}