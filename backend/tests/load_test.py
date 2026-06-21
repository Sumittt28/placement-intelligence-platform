"""
Load test script for Placement Intelligence Platform.
Tests concurrent user simulation for 100-200 users.

Usage:
    # Install: pip install httpx
    # Run against local:  python tests/load_test.py http://localhost:8000
    # Run against prod:   python tests/load_test.py https://placement-intel-api.onrender.com

Output: Response times, error rates, throughput stats.
"""
import asyncio
import time
import sys
import uuid
import statistics
from dataclasses import dataclass, field
from httpx import AsyncClient


@dataclass
class LoadTestStats:
    """Track response times and errors."""
    request_times: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    status_codes: dict = field(default_factory=dict)

    def record(self, endpoint: str, status: int, duration_ms: float):
        self.request_times.append((endpoint, duration_ms))
        self.status_codes[status] = self.status_codes.get(status, 0) + 1
        if status >= 400:
            self.errors.append((endpoint, status, duration_ms))

    def summary(self) -> str:
        if not self.request_times:
            return "No requests recorded."

        times = [t[1] for t in self.request_times]
        lines = [
            "\n" + "=" * 60,
            "  LOAD TEST RESULTS",
            "=" * 60,
            f"  Total requests:    {len(self.request_times)}",
            f"  Successful:        {len(self.request_times) - len(self.errors)}",
            f"  Failed:            {len(self.errors)}",
            f"  Error rate:        {len(self.errors) / len(self.request_times) * 100:.1f}%",
            "",
            f"  Avg response:      {statistics.mean(times):.0f}ms",
            f"  Median response:   {statistics.median(times):.0f}ms",
            f"  P95 response:      {sorted(times)[int(len(times) * 0.95)]:.0f}ms",
            f"  P99 response:      {sorted(times)[int(len(times) * 0.99)]:.0f}ms",
            f"  Min response:      {min(times):.0f}ms",
            f"  Max response:      {max(times):.0f}ms",
            "",
            "  Status codes:",
        ]
        for code, count in sorted(self.status_codes.items()):
            lines.append(f"    {code}: {count}")

        if self.errors:
            lines.append("")
            lines.append("  Errors (first 10):")
            for ep, status, dur in self.errors[:10]:
                lines.append(f"    {ep} → {status} ({dur:.0f}ms)")

        lines.append("=" * 60)
        return "\n".join(lines)


async def simulate_user(client: AsyncClient, base_url: str, user_num: int, stats: LoadTestStats):
    """Simulate a single user's typical session."""
    email = f"loadtest_{uuid.uuid4().hex[:8]}@test.com"
    token = None

    async def timed_request(method: str, path: str, **kwargs):
        """Make a request and record timing."""
        start = time.time()
        try:
            if method == "GET":
                r = await client.get(f"{base_url}{path}", **kwargs)
            elif method == "POST":
                r = await client.post(f"{base_url}{path}", **kwargs)
            elif method == "PUT":
                r = await client.put(f"{base_url}{path}", **kwargs)
            else:
                return None
            duration_ms = (time.time() - start) * 1000
            stats.record(path, r.status_code, duration_ms)
            return r
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            stats.record(path, 0, duration_ms)
            stats.errors.append((path, 0, duration_ms))
            return None

    headers = {}

    # 1. Register
    r = await timed_request("POST", "/api/v1/auth/register", json={
        "email": email,
        "password": "LoadTest123!",
        "full_name": f"Load Test User {user_num}",
    })
    if r and r.status_code == 200:
        token = r.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
    else:
        return  # Can't continue without auth

    # 2. Dashboard (most common action)
    await timed_request("GET", "/api/v1/dashboard", headers=headers)

    # 3. List companies
    await timed_request("GET", "/api/v1/companies", headers=headers)

    # 4. View a company (if available)
    r = await timed_request("GET", "/api/v1/companies", headers=headers)
    if r and r.status_code == 200:
        companies = r.json().get("data", [])
        if companies:
            cid = companies[0]["id"]
            await timed_request("GET", f"/api/v1/companies/{cid}", headers=headers)

    # 5. Check weaknesses
    await timed_request("GET", "/api/v1/weaknesses", headers=headers)

    # 6. Check readiness
    await timed_request("GET", "/api/v1/readiness", headers=headers)

    # 7. Search
    await timed_request("GET", "/api/v1/search?q=python", headers=headers)

    # 8. Get profile
    await timed_request("GET", "/api/v1/users/me", headers=headers)

    # 9. Dashboard again (should be cached)
    await timed_request("GET", "/api/v1/dashboard", headers=headers)


async def run_load_test(base_url: str, num_users: int = 50, batch_size: int = 10):
    """Run load test with concurrent users."""
    print(f"\n🚀 Load Test: {num_users} users against {base_url}")
    print(f"   Batch size: {batch_size} concurrent users")
    print(f"   Each user: register → dashboard → companies → search → profile")
    print()

    stats = LoadTestStats()

    # Health check first
    async with AsyncClient(timeout=30) as client:
        try:
            r = await client.get(f"{base_url}/health")
            if r.status_code != 200:
                print(f"❌ Health check failed: {r.status_code}")
                return
            print(f"✅ Server healthy: {r.json()}")
        except Exception as e:
            print(f"❌ Cannot reach server: {e}")
            return

    start_time = time.time()

    # Process users in batches
    async with AsyncClient(timeout=30) as client:
        for batch_start in range(0, num_users, batch_size):
            batch_end = min(batch_start + batch_size, num_users)
            batch_num = batch_start // batch_size + 1
            total_batches = (num_users + batch_size - 1) // batch_size

            print(f"  Batch {batch_num}/{total_batches}: Users {batch_start + 1}-{batch_end}...", end=" ")

            tasks = [
                simulate_user(client, base_url, i, stats)
                for i in range(batch_start, batch_end)
            ]
            await asyncio.gather(*tasks)
            print(f"✅ ({len(stats.request_times)} total requests)")

    total_time = time.time() - start_time
    print(f"\n  Total time: {total_time:.1f}s")
    print(f"  Throughput: {len(stats.request_times) / total_time:.1f} requests/sec")
    print(stats.summary())


if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    num_users = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    batch_size = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    asyncio.run(run_load_test(base_url, num_users, batch_size))
