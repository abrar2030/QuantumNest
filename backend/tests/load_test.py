import os
import time
import asyncio
import pytest
from locust import HttpUser, task, between
from fastapi.testclient import TestClient
import multiprocessing
import uvicorn
import sys
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Test server configuration
HOST = "127.0.0.1"
PORT = 8000

def run_server():
    """Run FastAPI server for load testing"""
    uvicorn.run(app, host=HOST, port=PORT)

class LoadTest:
    """Load test for QuantumNest API"""
    
    def __init__(self, host=f"http://{HOST}:{PORT}", num_users=10, spawn_rate=1, run_time=60):
        self.host = host
        self.num_users = num_users
        self.spawn_rate = spawn_rate
        self.run_time = run_time
        self.server_process = None
        
    def setup(self):
        """Start server in separate process"""
        logger.info("Starting server for load testing...")
        self.server_process = multiprocessing.Process(target=run_server)
        self.server_process.start()
        
        # Wait for server to start
        time.sleep(2)
        
        # Check if server is running
        try:
            response = requests.get(f"{self.host}/health")
            if response.status_code != 200:
                logger.error(f"Server health check failed: {response.status_code}")
                self.teardown()
                return False
            logger.info("Server started successfully")
            return True
        except Exception as e:
            logger.error(f"Error connecting to server: {str(e)}")
            self.teardown()
            return False
    
    def teardown(self):
        """Stop server"""
        if self.server_process:
            logger.info("Stopping server...")
            self.server_process.terminate()
            self.server_process.join()
            logger.info("Server stopped")
    
    def run_load_test(self):
        """Run load test using direct HTTP requests"""
        if not self.setup():
            return False
        
        try:
            logger.info(f"Starting load test with {self.num_users} concurrent users...")
            
            # Track metrics
            response_times = []
            error_count = 0
            request_count = 0
            
            # Simulate users
            start_time = time.time()
            
            # Create session with authentication
            session = requests.Session()
            
            # Mock authentication for testing
            session.headers.update({"Authorization": "Bearer test_token"})
            
            while time.time() - start_time < self.run_time:
                # Simulate multiple concurrent users
                processes = []
                for _ in range(self.num_users):
                    p = multiprocessing.Process(
                        target=self._simulate_user_requests, 
                        args=(session, response_times, error_count, request_count)
                    )
                    processes.append(p)
                    p.start()
                
                # Wait for all processes to complete
                for p in processes:
                    p.join()
                
                # Small delay between batches
                time.sleep(0.5)
            
            # Calculate metrics
            total_time = time.time() - start_time
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            requests_per_second = request_count / total_time if total_time > 0 else 0
            error_rate = (error_count / request_count) * 100 if request_count > 0 else 0
            
            # Log results
            logger.info(f"Load test completed in {total_time:.2f} seconds")
            logger.info(f"Total requests: {request_count}")
            logger.info(f"Average response time: {avg_response_time:.2f} ms")
            logger.info(f"Requests per second: {requests_per_second:.2f}")
            logger.info(f"Error rate: {error_rate:.2f}%")
            
            # Return results
            return {
                "total_time": total_time,
                "total_requests": request_count,
                "avg_response_time": avg_response_time,
                "requests_per_second": requests_per_second,
                "error_rate": error_rate
            }
            
        except Exception as e:
            logger.error(f"Error during load test: {str(e)}")
            return False
        finally:
            self.teardown()
    
    def _simulate_user_requests(self, session, response_times, error_count, request_count):
        """Simulate user requests"""
        try:
            # Test health endpoint
            self._make_request(session, "GET", "/health", response_times, error_count, request_count)
            
            # Test AI prediction endpoint
            self._make_request(
                session, 
                "POST", 
                "/ai/predict/asset/AAPL", 
                response_times, 
                error_count, 
                request_count
            )
            
            # Test sentiment analysis endpoint
            self._make_request(
                session, 
                "POST", 
                "/ai/sentiment/asset/MSFT", 
                response_times, 
                error_count, 
                request_count
            )
            
            # Test market recommendations endpoint
            self._make_request(
                session, 
                "POST", 
                "/ai/recommendations/market", 
                response_times, 
                error_count, 
                request_count
            )
            
            # Test task status endpoint (with mock task ID)
            self._make_request(
                session, 
                "GET", 
                "/ai/tasks/test-task-id", 
                response_times, 
                error_count, 
                request_count
            )
            
        except Exception as e:
            logger.error(f"Error in user simulation: {str(e)}")
    
    def _make_request(self, session, method, endpoint, response_times, error_count, request_count):
        """Make HTTP request and track metrics"""
        try:
            start_time = time.time()
            
            if method == "GET":
                response = session.get(f"{self.host}{endpoint}")
            elif method == "POST":
                response = session.post(f"{self.host}{endpoint}")
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Track response time in milliseconds
            response_time = (time.time() - start_time) * 1000
            response_times.append(response_time)
            
            # Track request count
            request_count += 1
            
            # Check for errors
            if response.status_code >= 400:
                error_count += 1
                logger.warning(f"Request error: {method} {endpoint} - {response.status_code}")
            
        except Exception as e:
            error_count += 1
            request_count += 1
            logger.error(f"Request exception: {method} {endpoint} - {str(e)}")

def run_load_test():
    """Run load test with default parameters"""
    load_test = LoadTest(num_users=20, spawn_rate=2, run_time=30)
    results = load_test.run_load_test()
    return results

if __name__ == "__main__":
    results = run_load_test()
    print(json.dumps(results, indent=2))
