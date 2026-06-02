package shield

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

func TestVelocityCounter_BasicCountAndSum(t *testing.T) {
	vc := NewVelocityCounter()

	vc.Record("user:1:tx", 100_000)
	vc.Record("user:1:tx", 200_000)
	vc.Record("user:1:tx", 300_000)

	count, sum := vc.Count("user:1:tx", 1*time.Hour)
	if count != 3 {
		t.Errorf("expected count=3, got %d", count)
	}
	if sum != 600_000 {
		t.Errorf("expected sum=600000, got %d", sum)
	}
}

func TestVelocityCounter_EmptyKey(t *testing.T) {
	vc := NewVelocityCounter()

	count, sum := vc.Count("nonexistent", 1*time.Hour)
	if count != 0 || sum != 0 {
		t.Errorf("expected 0/0 for nonexistent key, got %d/%d", count, sum)
	}
}

func TestVelocityCounter_WindowFiltering(t *testing.T) {
	vc := &VelocityCounter{
		windows: make(map[string]*slidingWindow),
	}

	now := time.Now()
	w := &slidingWindow{
		entries: []vcEntry{
			{at: now.Add(-2 * time.Hour), amount: 100_000},  // outside 1h window
			{at: now.Add(-30 * time.Minute), amount: 200_000}, // inside
			{at: now.Add(-5 * time.Minute), amount: 300_000},  // inside
		},
	}
	vc.windows["user:test:tx"] = w

	count, sum := vc.Count("user:test:tx", 1*time.Hour)
	if count != 2 {
		t.Errorf("expected count=2 (only entries within 1h), got %d", count)
	}
	if sum != 500_000 {
		t.Errorf("expected sum=500000 (200k+300k), got %d", sum)
	}
}

func TestVelocityCounter_DifferentWindows(t *testing.T) {
	vc := &VelocityCounter{
		windows: make(map[string]*slidingWindow),
	}

	now := time.Now()
	w := &slidingWindow{
		entries: []vcEntry{
			{at: now.Add(-23 * time.Hour), amount: 1_000_000},
			{at: now.Add(-2 * time.Hour), amount: 500_000},
			{at: now.Add(-30 * time.Minute), amount: 200_000},
		},
	}
	vc.windows["user:test:tx"] = w

	// 1h window: only last entry
	count1h, sum1h := vc.Count("user:test:tx", 1*time.Hour)
	if count1h != 1 || sum1h != 200_000 {
		t.Errorf("1h window: expected 1/200000, got %d/%d", count1h, sum1h)
	}

	// 24h window: all entries
	count24h, sum24h := vc.Count("user:test:tx", 24*time.Hour)
	if count24h != 3 || sum24h != 1_700_000 {
		t.Errorf("24h window: expected 3/1700000, got %d/%d", count24h, sum24h)
	}

	// 3h window: last 2 entries
	count3h, sum3h := vc.Count("user:test:tx", 3*time.Hour)
	if count3h != 2 || sum3h != 700_000 {
		t.Errorf("3h window: expected 2/700000, got %d/%d", count3h, sum3h)
	}
}

func TestVelocityCounter_IndependentKeys(t *testing.T) {
	vc := NewVelocityCounter()

	vc.Record("user:A:tx", 100_000)
	vc.Record("user:A:tx", 200_000)
	vc.Record("user:B:tx", 500_000)

	countA, sumA := vc.Count("user:A:tx", 1*time.Hour)
	countB, sumB := vc.Count("user:B:tx", 1*time.Hour)

	if countA != 2 || sumA != 300_000 {
		t.Errorf("user A: expected 2/300000, got %d/%d", countA, sumA)
	}
	if countB != 1 || sumB != 500_000 {
		t.Errorf("user B: expected 1/500000, got %d/%d", countB, sumB)
	}
}

func TestVelocityCounter_ConcurrentAccess(t *testing.T) {
	vc := NewVelocityCounter()
	var wg sync.WaitGroup

	for i := 0; i < 50; i++ {
		wg.Add(2)
		go func(id int) {
			defer wg.Done()
			key := fmt.Sprintf("user:%d:tx", id)
			for j := 0; j < 500; j++ {
				vc.Record(key, int64(j*100))
			}
		}(i)
		go func(id int) {
			defer wg.Done()
			key := fmt.Sprintf("user:%d:tx", id)
			for j := 0; j < 500; j++ {
				vc.Count(key, 1*time.Hour)
			}
		}(i)
	}
	wg.Wait()

	count, _ := vc.Count("user:0:tx", 1*time.Hour)
	if count == 0 {
		t.Error("expected entries for user:0:tx after concurrent writes")
	}
}

func TestVelocityCounter_BoundedEntries(t *testing.T) {
	vc := NewVelocityCounter()
	for i := 0; i < 2000; i++ {
		vc.Record("overflow:tx", int64(i))
	}
	count, _ := vc.Count("overflow:tx", 24*time.Hour)
	if count > maxEntriesPerKey {
		t.Errorf("expected max %d entries, got %d", maxEntriesPerKey, count)
	}
}
