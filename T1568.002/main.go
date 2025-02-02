package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"math/rand"
	"net"
	"os"
	"strings"
	"time"
)

// GenerateDGA generates a list of DGA-based domains with a more complex logic for randomness.
func GenerateDGA(seed string, count int) []string {
	rand.Seed(time.Now().UnixNano())
	domains := make([]string, count)

	tlds := []string{".com", ".net", ".org", ".info", ".biz", ".io", ".xyz"} // A variety of TLDs

	for i := 0; i < count; i++ {
		// Create a unique string based on the seed, the current index, and some randomness
		randomPart := fmt.Sprintf("%d", rand.Int63())
		input := fmt.Sprintf("%s%d%s", seed, i, randomPart)

		// Generate a SHA256 hash of the input for stronger randomness
		hash := sha256.Sum256([]byte(input))
		hashStr := hex.EncodeToString(hash[:])

		// Incorporate parts of the hash and additional randomness into the domain name
		prefix := hashStr[:8]                    // First 8 characters of the hash
		middle := hashStr[24:32]                 // Middle part of the hash
		suffix := strings.ToLower(hashStr[48:]) // Use a longer section for the suffix
		tld := tlds[rand.Intn(len(tlds))]       // Randomly select a TLD
		domain := fmt.Sprintf("%s%s%s%s", prefix, middle, suffix, tld)
		domains[i] = domain
	}

	return domains
}

// ResolveDomains resolves a list of domains and logs the results to stdout.
func ResolveDomains(domains []string) {
	for _, domain := range domains {
		ips, err := net.LookupHost(domain)
		if err != nil {
			fmt.Fprintf(os.Stdout, "[ERROR] Failed to resolve domain %s: %v\n", domain, err)
			continue
		}
		fmt.Fprintf(os.Stdout, "[INFO] Domain %s resolved to: %v\n", domain, ips)
	}
}

func main() {
	// Seed for DGA
	seed := fmt.Sprintf("dga-seed-%d", time.Now().UnixNano())

	// Number of domains to generate
	numDomains := 10

	// Generate domains
	domains := GenerateDGA(seed, numDomains)
	fmt.Println("Generated DGA domains:")
	for _, domain := range domains {
		fmt.Println(domain)
	}

	fmt.Println("\nResolving domains...")

	// Resolve generated domains
	ResolveDomains(domains)
}