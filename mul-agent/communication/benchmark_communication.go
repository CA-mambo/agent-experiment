package main

import (
	"fmt"
	"math/rand"
	"sync"
	"time"
)

// Simulated Handler Functions
func mockACPHandler(id string, wg *sync.WaitGroup) {
	defer wg.Done()
	// Simulate network + x402 verification latency
	time.Sleep(time.Duration(50+rand.Intn(100)) * time.Millisecond)
}

func mockHandoffHandler(id string, wg *sync.WaitGroup) {
	defer wg.Done()
	// Simulate deep context copy + guardrails latency
	time.Sleep(time.Duration(100+rand.Intn(100)) * time.Millisecond)
}

func mockPubSubHandler(id string, wg *sync.WaitGroup) {
	defer wg.Done()
	// Simulate bus routing latency (very low)
	time.Sleep(time.Duration(20+rand.Intn(60)) * time.Millisecond)
}

func mockStdioHandler(id string, wg *sync.WaitGroup) {
	defer wg.Done()
	// Simulate subprocess spawn + IO latency
	time.Sleep(time.Duration(50+rand.Intn(70)) * time.Millisecond)
}

type Benchmark struct {
	Name string
	Handler func(string, *sync.WaitGroup)
	ConcurrencyLevels []int
}

func (b *Benchmark) RunSingle(n int) time.Duration {
	var wg sync.WaitGroup
	start := time.Now()
	for i := 0; i < n; i++ {
		wg.Add(1)
		go b.Handler(fmt.Sprintf("req_%d", i), &wg)
	}
	wg.Wait()
	return time.Since(start)
}

func (b *Benchmark) Benchmark() {
	fmt.Printf("\n[BENCHMARK] %s\n", b.Name)
	fmt.Printf("%-15s | %-12s | %-18s\n", "Concurrency", "Avg Time (ms)", "Throughput (req/s)")
	fmt.Println("--------------------------------------------------")

	for _, level := range b.ConcurrencyLevels {
		var totalDuration time.Duration
		iterations := 3
		for i := 0; i < iterations; i++ {
			totalDuration += b.RunSingle(level)
		}
		avgDuration := totalDuration / time.Duration(iterations)
		avgMs := float64(avgDuration.Microseconds()) / 1000.0
		throughput := float64(level) / avgDuration.Seconds()
		fmt.Printf("%-15d | %-12.2f | %-18.2f\n", level, avgMs, throughput)
	}
	fmt.Println("--------------------------------------------------")
}

func main() {
	// rand.Seed is not needed in Go 1.20+, math/rand is auto-seeded

	benchmarks := []Benchmark{
		{"OpenClaw (ACP + x402)", mockACPHandler, []int{1, 5, 10, 20, 50, 100}},
		{"Codex (Handoff + Guardrails)", mockHandoffHandler, []int{1, 5, 10, 20, 50, 100}},
		{"Hermes (Pub/Sub Bus)", mockPubSubHandler, []int{1, 5, 10, 20, 50, 100}},
		{"OpenCode (Stdio Spawn)", mockStdioHandler, []int{1, 5, 10, 20, 50, 100}},
	}

	fmt.Println("==================================================")
	fmt.Println("  Multi-Agent Communication Mechanisms Benchmark (Go)")
	fmt.Println("==================================================")

	for _, b := range benchmarks {
		b.Benchmark()
	}
}
