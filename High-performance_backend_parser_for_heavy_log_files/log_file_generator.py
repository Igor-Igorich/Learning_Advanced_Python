import random


def generate_sample_log_file(file_path: str, num_lines: int = 150_000) -> None:

    methods = ["GET", "POST", "PUT", "DELETE"]
    endpoints = [
        "/api/v1/users",
        "/api/v1/orders",
        "/api/v1/products",
        "/api/v1/auth",
    ]
    statuses = [200, 201, 200, 200, 400, 404, 500, 503]

    with open(file_path, "w", encoding="utf-8") as f:
        for i in range(num_lines):
            ip = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
            timestamp = f"2026-08-08T15:{i % 60:02d}:{(i // 60) % 60:02d}Z"
            method = random.choice(methods)
            endpoint = random.choice(endpoints)
            status = random.choice(statuses)
            latency = random.randint(10, 1000)

            f.write(
                f"{timestamp} | {ip} | {method} | {endpoint} | {status} | {latency}\n"
            )
