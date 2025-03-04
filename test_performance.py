import requests
import time
import concurrent.futures
import pandas as pd
import matplotlib.pyplot as plt
import psutil
from datetime import datetime

class ResourcePerformanceTester:
    def __init__(self):
        self.endpoints = {
            'monolithic': 'http://your-ec2-instance:5000',
            'iaas': {
                'creator': 'http://your-creator-alb',
                'redirector': 'http://your-redirector-alb'
            },
            'serverless': 'https://your-api-gateway-url/prod'
        }
        self.test_url = "https://www.example.com"
        self.results = []

    def measure_system_metrics(self, url):
        metrics = {}
        
        # Initial measurements
        start_time = time.time()
        initial_cpu = psutil.cpu_percent(interval=1)
        initial_memory = psutil.virtual_memory().percent
        initial_network = psutil.net_io_counters()

        try:
            # Make request and measure
            response = requests.get(url, timeout=30)
            content_size = len(response.content)
            
            # Final measurements
            end_time = time.time()
            final_cpu = psutil.cpu_percent(interval=1)
            final_memory = psutil.virtual_memory().percent
            final_network = psutil.net_io_counters()

            # Calculate metrics
            elapsed_time = end_time - start_time
            network_bytes_sent = final_network.bytes_sent - initial_network.bytes_sent
            network_bytes_recv = final_network.bytes_recv - initial_network.bytes_recv

            metrics = {
                'timestamp': datetime.now(),
                'response_time': elapsed_time * 1000,  # ms
                'cpu_usage': final_cpu - initial_cpu,
                'memory_usage': final_memory - initial_memory,
                'network_sent': network_bytes_sent,
                'network_received': network_bytes_recv,
                'content_size': content_size,
                'throughput': content_size / elapsed_time if elapsed_time > 0 else 0,
                'success': response.status_code in [200, 301, 302]
            }

        except Exception as e:
            print(f"Error measuring metrics: {str(e)}")
            metrics = {
                'timestamp': datetime.now(),
                'response_time': 0,
                'cpu_usage': 0,
                'memory_usage': 0,
                'network_sent': 0,
                'network_received': 0,
                'content_size': 0,
                'throughput': 0,
                'success': False
            }

        return metrics

    def run_test(self, architecture, num_requests, concurrency):
        print(f"\nTesting {architecture} architecture...")
        
        if architecture == 'monolithic':
            url = f"{self.endpoints['monolithic']}/create/{self.test_url}"
        elif architecture == 'iaas':
            url = f"{self.endpoints['iaas']['creator']}/create/{self.test_url}"
        else:  # serverless
            url = f"{self.endpoints['serverless']}/create/{self.test_url}"

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(self.measure_system_metrics, url) 
                      for _ in range(num_requests)]
            
            batch_results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            for result in batch_results:
                result['architecture'] = architecture
                self.results.append(result)

    def analyze_results(self):
        df = pd.DataFrame(self.results)
        
        # Create visualizations
        plt.figure(figsize=(15, 10))

        # CPU Usage
        plt.subplot(2, 2, 1)
        df.boxplot(column='cpu_usage', by='architecture')
        plt.title('CPU Usage by Architecture')
        plt.ylabel('CPU Usage (%)')

        # Memory Usage
        plt.subplot(2, 2, 2)
        df.boxplot(column='memory_usage', by='architecture')
        plt.title('Memory Usage by Architecture')
        plt.ylabel('Memory Usage (%)')

        # Network Throughput
        plt.subplot(2, 2, 3)
        df.groupby('architecture')[['network_sent', 'network_received']].mean().plot(kind='bar')
        plt.title('Average Network I/O')
        plt.ylabel('Bytes')

        # Request Throughput
        plt.subplot(2, 2, 4)
        df.boxplot(column='throughput', by='architecture')
        plt.title('Request Throughput')
        plt.ylabel('Bytes/second')

        plt.tight_layout()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.savefig(f'resource_metrics_{timestamp}.png')
        
        # Calculate statistics
        stats = df.groupby('architecture').agg({
            'cpu_usage': ['mean', 'max'],
            'memory_usage': ['mean', 'max'],
            'network_sent': ['mean', 'sum'],
            'network_received': ['mean', 'sum'],
            'throughput': ['mean', 'max'],
            'success': 'mean'
        }).round(2)

        # Save stats to CSV
        stats.to_csv(f'resource_metrics_{timestamp}.csv')
        
        return stats

def main():
    tester = ResourcePerformanceTester()
    
    # Test scenarios
    scenarios = [
        (100, 10),    # Light load
        (500, 50),    # Medium load
        (1000, 100)   # Heavy load
    ]
    
    architectures = ['monolithic', 'iaas', 'serverless']
    
    for num_requests, concurrency in scenarios:
        print(f"\nRunning test scenario: {num_requests} requests with {concurrency} concurrent users")
        for arch in architectures:
            tester.run_test(arch, num_requests, concurrency)
    
    # Analyze and display results
    results = tester.analyze_results()
    print("\nResource Usage Summary:")
    print(results)
    print("\nCheck the generated CSV file and PNG image for detailed metrics.")

if __name__ == "__main__":
    main()
