#!/usr/bin/env python3
import requests
import sys
import json
from datetime import datetime

class ArabicPoetryAPITester:
    def __init__(self, base_url="https://poetryverse.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.sample_poet_id = None
        self.sample_poem_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list) and len(response_data) > 0:
                        print(f"   Response: Found {len(response_data)} items")
                    elif isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_init_sample_data(self):
        """Initialize sample data"""
        success, response = self.run_test(
            "Initialize Sample Data",
            "POST", 
            "init-data",
            200
        )
        return success

    def test_get_poets(self):
        """Test getting all poets"""
        success, response = self.run_test(
            "Get All Poets",
            "GET",
            "poets",
            200
        )
        if success and isinstance(response, list) and len(response) > 0:
            self.sample_poet_id = response[0].get('id')
            print(f"   Found sample poet: {response[0].get('name')} (ID: {self.sample_poet_id})")
        return success

    def test_get_single_poet(self):
        """Test getting a single poet"""
        if not self.sample_poet_id:
            print("❌ Skipped - No sample poet ID available")
            return False
            
        return self.run_test(
            "Get Single Poet",
            "GET",
            f"poets/{self.sample_poet_id}",
            200
        )[0]

    def test_get_poems(self):
        """Test getting all poems"""
        success, response = self.run_test(
            "Get All Poems",
            "GET",
            "poems",
            200
        )
        if success and isinstance(response, list) and len(response) > 0:
            self.sample_poem_id = response[0].get('id')
            print(f"   Found sample poem: {response[0].get('title')} (ID: {self.sample_poem_id})")
        return success

    def test_get_single_poem(self):
        """Test getting a single poem"""
        if not self.sample_poem_id:
            print("❌ Skipped - No sample poem ID available")
            return False
            
        return self.run_test(
            "Get Single Poem",
            "GET",
            f"poems/{self.sample_poem_id}",
            200
        )[0]

    def test_search_functionality(self):
        """Test search functionality"""
        test_cases = [
            ("المتنبي", "Search for poet name"),
            ("العزم", "Search for word in poem"),
            ("حكمة", "Search for theme")
        ]
        
        all_passed = True
        for query, description in test_cases:
            success, response = self.run_test(
                f"Search - {description}",
                "GET",
                "search",
                200,
                params={"q": query}
            )
            if success:
                poets_count = len(response.get('poets', []))
                poems_count = len(response.get('poems', []))
                print(f"   Found {poets_count} poets, {poems_count} poems")
            all_passed = all_passed and success
            
        return all_passed

    def test_word_explanation(self):
        """Test the main AI word explanation feature"""
        print("\n🎯 Testing MAIN FEATURE: AI Word Explanation")
        
        test_cases = [
            {
                "word": "العزم",
                "context": "على قدر أهل العزم تأتي العزائم",
                "poem_title": "على قدر أهل العزم",
                "poet_name": "أبو الطيب المتنبي"
            },
            {
                "word": "المكارم", 
                "context": "وتأتي على قدر الكرام المكارم",
                "poem_title": "على قدر أهل العزم",
                "poet_name": "أبو الطيب المتنبي"
            },
            {
                "word": "العظائم",
                "context": "وتصغر في عين العظيم العظائم", 
                "poem_title": "على قدر أهل العزم",
                "poet_name": "أبو الطيب المتنبي"
            }
        ]
        
        all_passed = True
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   Test Case {i}: Explaining word '{test_case['word']}'")
            success, response = self.run_test(
                f"AI Word Explanation - {test_case['word']}",
                "POST",
                "explain-word",
                200,
                data=test_case
            )
            
            if success and isinstance(response, dict):
                explanation = response.get('explanation', '')
                if explanation and len(explanation) > 10:
                    print(f"   ✅ AI Explanation received: {explanation[:100]}...")
                else:
                    print(f"   ❌ Empty or invalid explanation: {explanation}")
                    success = False
            
            all_passed = all_passed and success
            
        return all_passed

    def test_poems_by_poet(self):
        """Test getting poems by specific poet"""
        if not self.sample_poet_id:
            print("❌ Skipped - No sample poet ID available")
            return False
            
        return self.run_test(
            "Get Poems by Poet",
            "GET",
            "poems",
            200,
            params={"poet_id": self.sample_poet_id}
        )[0]

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Arabic Poetry Platform API Tests")
        print("=" * 60)
        
        # Test basic connectivity
        print("\n📡 CONNECTIVITY TESTS")
        self.test_root_endpoint()
        
        # Initialize data
        print("\n🔧 DATA INITIALIZATION")
        self.test_init_sample_data()
        
        # Test core endpoints
        print("\n📚 CORE API TESTS")
        self.test_get_poets()
        self.test_get_single_poet()
        self.test_get_poems()
        self.test_get_single_poem()
        self.test_poems_by_poet()
        
        # Test search functionality
        print("\n🔍 SEARCH FUNCTIONALITY")
        self.test_search_functionality()
        
        # Test main AI feature
        print("\n🤖 AI INTEGRATION TESTS")
        self.test_word_explanation()
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 FINAL RESULTS: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend is working correctly.")
            return 0
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} test(s) failed. Please check the issues above.")
            return 1

def main():
    tester = ArabicPoetryAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())