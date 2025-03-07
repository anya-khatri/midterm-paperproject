import requests
import time
import concurrent.futures
import pandas as pd
import psutil
import numpy as np
from datetime import datetime

class ResourcePerformanceTester:
    def __init__(self):
        self.endpoints = {
            'monolithic': 'http://your-ec2-instance:5000',
            'iaas': {
                'creator': 'http://your-creator-alb',
                'redirector': 'http://your-redirector-alb'
            },
            'paas': 'http://your-elastic-beanstalk-env.region.elasticbeanstalk.com',
            'serverless': 'https://your-api-gateway-url/prod'
        }
        self.test_url = "https://www.example.com"
        self.results = []
        self.scenarios = {
            'light': {'requests': 100, 'concurrency': 10},
            'medium': {'requests': 500, 'concurrency': 50},
            'heavy': {'requests': 1000, 'concurrency': 100}
        }

    def measure_system_metrics(self, url, scenario_name):
        latencies = []
        start_time = time.time()
        initial_cpu = psutil.cpu_percent(interval=1)
        initial_memory = psutil.virtual_memory().percent
        initial_network = psutil.net_io_counters()

        try:
            response = requests.get(url, timeout=30)
            latencies.append(response.elapsed.total_seconds() * 1000)  # Convert to ms
            content_size = len(response.content)
            
            end_time = time.time()
            final_cpu = psutil.cpu_percent(interval=1)
            final_memory = psutil.virtual_memory().percent
            final_network = psutil.net_io_counters()

            metrics = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'cpu_usage_mean': final_cpu - initial_cpu,
                'cpu_usage_max': max(final_cpu, initial_cpu),
                'memory_usage_mean': final_memory - initial_memory,
                'memory_usage_max': max(final_memory, initial_memory),
                'network_sent': final_network.bytes_sent - initial_network.bytes_sent,
                'network_received': final_network.bytes_recv - initial_network.bytes_recv,
                'throughput_mean': content_size / (end_time - start_time) if end_time > start_time else 0,
                'throughput_max': content_size / min(latencies) if latencies else 0,
                'success_rate': 100 if response.status_code in [200, 301, 302] else 0,
                'latency_mean': np.mean(latencies),
                'latency_p95': np.percentile(latencies, 95)
            }

        except Exception as e:
            print(f"Error measuring metrics: {str(e)}")
            metrics = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'cpu_usage_mean': 0,
                'cpu_usage_max': 0,
                'memory_usage_mean': 0,
                'memory_usage_max': 0,
                'network_sent': 0,
                'network_received': 0,
                'throughput_mean': 0,
                'throughput_max': 0,
                'success_rate': 0,
                'latency_mean': 0,
                'latency_p95': 0
            }

        return metrics

    def run_test(self, architecture, scenario_name):
        print(f"\nTesting {architecture} architecture with {scenario_name} load...")
        
        scenario = self.scenarios[scenario_name]
        if architecture == 'monolithic':
            url = f"{self.endpoints['monolithic']}/create/{self.test_url}"
        elif architecture == 'iaas':
            url = f"{self.endpoints['iaas']['creator']}/create/{self.test_url}"
        elif architecture == 'paas':
            url = f"{self.endpoints['paas']}/create/{self.test_url}"
        else:  # serverless
            url = f"{self.endpoints['serverless']}/create/{self.test_url}"

        with concurrent.futures.ThreadPoolExecutor(max_workers=scenario['concurrency']) as executor:
            futures = [executor.submit(self.measure_system_metrics, url, scenario_name) 
                      for _ in range(scenario['requests'])]
            
            batch_results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            # Aggregate results
            aggregate = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'architecture': architecture,
                'scenario': scenario_name,
                'requests': scenario['requests'],
                'concurrency': scenario['concurrency']
            }
            
            metrics = pd.DataFrame(batch_results)
            aggregate.update({
                'cpu_usage_mean': metrics['cpu_usage_mean'].mean(),
                'cpu_usage_max': metrics['cpu_usage_max'].max(),
                'memory_usage_mean': metrics['memory_usage_mean'].mean(),
                'memory_usage_max': metrics['memory_usage_max'].max(),
                'network_sent': metrics['network_sent'].sum(),
                'network_received': metrics['network_received'].sum(),
                'throughput_mean': metrics['throughput_mean'].mean(),
                'throughput_max': metrics['throughput_max'].max(),
                'success_rate': metrics['success_rate'].mean(),
                'latency_mean': metrics['latency_mean'].mean(),
                'latency_p95': metrics['latency_p95'].max()
            })
            
            self.results.append(aggregate)

    def save_results(self):
        df = pd.DataFrame(self.results)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'performance_metrics_{timestamp}.csv'
        
        columns = [
            'timestamp', 'architecture', 'scenario', 'requests', 'concurrency',
            'cpu_usage_mean', 'cpu_usage_max', 'memory_usage_mean', 'memory_usage_max',
            'network_sent', 'network_received', 'throughput_mean', 'throughput_max',
            'success_rate', 'latency_mean', 'latency_p95'
        ]
        
        df = df[columns]
        df.to_csv(filename, index=False)
        return filename

def main():
    tester = ResourcePerformanceTester()
    architectures = ['monolithic', 'iaas', 'paas', 'serverless']
    scenarios = ['light', 'medium', 'heavy']
    
    for arch in architectures:
        for scenario in scenarios:
            tester.run_test(arch, scenario)
    
    filename = tester.save_results()
    print(f"\nTest complete! Results saved to {filename}")

if __name__ == "__main__":
    main()
