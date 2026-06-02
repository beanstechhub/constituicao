package shield

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"testing"
	"time"
)

func init() {
	slog.SetDefault(slog.New(slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{Level: slog.LevelError})))
}

func BenchmarkEvaluate(b *testing.B) {
	s := New()
	tx := &Transaction{
		ID:          "tx_bench",
		UserID:      "usr_bench",
		Type:        "pix_out",
		Amount:      150_000,
		Currency:    "BRL",
		Destination: "dest_bench",
		IP:          "10.0.0.1",
		CreatedAt:   time.Now(),
	}
	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		s.Evaluate(ctx, tx)
	}
}

func BenchmarkEvaluateHighAmount(b *testing.B) {
	s := New()
	tx := &Transaction{
		ID:          "tx_bench_high",
		UserID:      "usr_bench_high",
		Type:        "pix_out",
		Amount:      6_000_000,
		Currency:    "BRL",
		Destination: "new_dest",
		IP:          "10.0.0.2",
		CreatedAt:   time.Now(),
	}
	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		s.Evaluate(ctx, tx)
	}
}

func BenchmarkEvaluateWithMerchant(b *testing.B) {
	s := New()
	config := DefaultBettingConfig("bench_merchant")
	tx := &Transaction{
		ID:        "tx_bench_merchant",
		UserID:    "usr_bench_m",
		Type:      "pix_in",
		Amount:    100_000,
		Currency:  "BRL",
		IP:        "10.0.0.3",
		CreatedAt: time.Now(),
	}
	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		s.EvaluateWithMerchant(ctx, tx, config)
	}
}

func BenchmarkEvaluateWithVelocityLoad(b *testing.B) {
	s := New()
	ctx := context.Background()

	// Pre-load velocity counter with realistic data
	for i := 0; i < 100; i++ {
		s.velocity.Record(fmt.Sprintf("user:loaded_%d:tx", i%10), int64(i*10000))
	}

	tx := &Transaction{
		ID:          "tx_bench_loaded",
		UserID:      "loaded_5",
		Type:        "pix_out",
		Amount:      200_000,
		Currency:    "BRL",
		Destination: "dest_loaded",
		IP:          "10.0.0.5",
		CreatedAt:   time.Now(),
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		s.Evaluate(ctx, tx)
	}
}

func BenchmarkVelocityCounterRecord(b *testing.B) {
	vc := NewVelocityCounter()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		vc.Record("user:bench:tx", 100_000)
	}
}

func BenchmarkVelocityCounterCount(b *testing.B) {
	vc := NewVelocityCounter()
	for i := 0; i < 1000; i++ {
		vc.Record("user:bench:tx", int64(i*1000))
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		vc.Count("user:bench:tx", 1*time.Hour)
	}
}
