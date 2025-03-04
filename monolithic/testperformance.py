import requests
import time
import concurrent.futures
import statistics

def make_request(url):
    start_time = time.time()
    try:
        response = requests.get(url)
        end_time = time.time()
        return {
            'time': end_time - start_time,
            'status': response.status_code,
            'success': True
        }
    except Exception as e:
        return {
            'time': 0,
            'status': 0,
            'success': False
        }

def run_test(url, num_requests, concurrency):
    print(f"\nTesting URL: {url}")
    print(f"Number of requests: {num_requests}")
    print(f"Concurrency level: {concurrency}")
    print("-" * 50)

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(make_request, url) for _ in range(num_requests)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    successful_times = [r['time'] for r in results if r['success']]
    
    if successful_times:
        avg_time = statistics.mean(successful_times)
        median_time = statistics.median(successful_times)
        total_time = time.time() - start_time
        
        print(f"\nResults:")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Average response time: {avg_time*1000:.2f} ms")
        print(f"Median response time: {median_time*1000:.2f} ms")
        print(f"Min response time: {min(successful_times)*1000:.2f} ms")
        print(f"Max response time: {max(successful_times)*1000:.2f} ms")
        print(f"Requests per second: {num_requests/total_time:.2f}")
        print(f"Successful requests: {len(successful_times)}/{num_requests}")
    else:
        print("No successful requests")

if __name__ == "__main__":
    base_url = "http://localhost:5000"
    
    # Test homepage
    run_test(f"{base_url}/", 100, 10)
    
    # Test URL creation
    run_test(f"{base_url}/create/https://www.example.com", 100, 10)
    
    # Test URL redirect (replace ABC123 with an actual short code)
    # run_test(f"{base_url}/ABC123", 100, 10)
