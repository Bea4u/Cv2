import requests
import sys
from datetime import datetime, timedelta
import json

class VerdeWellnessAPITester:
    def __init__(self, base_url="https://health-balance-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.booking_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
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
        """Test root endpoint"""
        success, response = self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_get_services(self):
        """Test getting all services"""
        success, response = self.run_test(
            "Get Services",
            "GET", 
            "api/services",
            200
        )
        
        if success:
            # Verify we have 3 services with correct data
            services = response
            if len(services) == 3:
                print("   ✅ Found 3 services as expected")
                
                # Check specific services
                service_titles = [s['title'] for s in services]
                expected_titles = ['Premium Personal Training', 'Holistic Nutrition Coaching', 'Executive Wellness Package']
                expected_prices = [120, 200, 450]
                
                for i, title in enumerate(expected_titles):
                    if title in service_titles:
                        service = next(s for s in services if s['title'] == title)
                        if service['price'] == expected_prices[i]:
                            print(f"   ✅ {title}: ${service['price']} - Correct")
                        else:
                            print(f"   ❌ {title}: Expected ${expected_prices[i]}, got ${service['price']}")
                    else:
                        print(f"   ❌ Missing service: {title}")
            else:
                print(f"   ❌ Expected 3 services, got {len(services)}")
                
        return success, response if success else []

    def test_get_availability(self):
        """Test getting availability for a future date"""
        # Test with a future date (August 16th, 2025)
        test_date = datetime(2025, 8, 16)
        date_str = test_date.isoformat()
        
        success, response = self.run_test(
            "Get Availability",
            "GET",
            "api/availability",
            200,
            params={"date": date_str}
        )
        
        if success:
            slots = response
            expected_slots = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]
            if isinstance(slots, list) and len(slots) > 0:
                print(f"   ✅ Found {len(slots)} available slots")
                print(f"   Available slots: {slots}")
                
                # Check if we have expected business hours
                for slot in expected_slots:
                    if slot in slots:
                        print(f"   ✅ {slot} - Available")
                    else:
                        print(f"   ⚠️  {slot} - Not available (might be booked)")
            else:
                print(f"   ❌ No available slots returned")
                
        return success, response if success else []

    def test_create_booking(self, services):
        """Test creating a booking"""
        if not services:
            print("   ❌ No services available for booking test")
            return False
            
        # Use Premium Personal Training service
        service = next((s for s in services if s['title'] == 'Premium Personal Training'), services[0])
        
        # Book for August 16th, 2025 at 10:00
        booking_data = {
            "service_id": service['id'],
            "service_title": service['title'],
            "date": "2025-08-16T10:00:00.000Z",
            "time": "10:00",
            "price": service['price'],
            "status": "confirmed"
        }
        
        success, response = self.run_test(
            "Create Booking",
            "POST",
            "api/bookings",
            200,
            data=booking_data
        )
        
        if success:
            self.booking_id = response.get('id')
            print(f"   ✅ Booking created with ID: {self.booking_id}")
            
            # Verify booking details
            if response.get('service_title') == service['title']:
                print(f"   ✅ Service title correct: {response.get('service_title')}")
            if response.get('price') == service['price']:
                print(f"   ✅ Price correct: ${response.get('price')}")
            if response.get('status') == 'confirmed':
                print(f"   ✅ Status correct: {response.get('status')}")
                
        return success

    def test_get_bookings(self):
        """Test getting all bookings"""
        success, response = self.run_test(
            "Get All Bookings",
            "GET",
            "api/bookings",
            200
        )
        
        if success:
            bookings = response
            print(f"   ✅ Found {len(bookings)} bookings")
            
            if self.booking_id:
                # Check if our booking is in the list
                our_booking = next((b for b in bookings if b.get('id') == self.booking_id), None)
                if our_booking:
                    print(f"   ✅ Our booking found in the list")
                else:
                    print(f"   ❌ Our booking not found in the list")
                    
        return success

    def test_get_specific_booking(self):
        """Test getting a specific booking by ID"""
        if not self.booking_id:
            print("   ❌ No booking ID available for specific booking test")
            return False
            
        success, response = self.run_test(
            "Get Specific Booking",
            "GET",
            f"api/bookings/{self.booking_id}",
            200
        )
        
        if success:
            if response.get('id') == self.booking_id:
                print(f"   ✅ Booking ID matches: {response.get('id')}")
            if response.get('status') == 'confirmed':
                print(f"   ✅ Booking status: {response.get('status')}")
                
        return success

    def test_availability_after_booking(self):
        """Test that availability is updated after booking"""
        test_date = datetime(2025, 8, 16)
        date_str = test_date.isoformat()
        
        success, response = self.run_test(
            "Get Availability After Booking",
            "GET",
            "api/availability",
            200,
            params={"date": date_str}
        )
        
        if success:
            slots = response
            if "10:00" not in slots:
                print("   ✅ 10:00 slot no longer available (correctly booked)")
            else:
                print("   ❌ 10:00 slot still available (booking may not have worked)")
                
        return success

def main():
    print("🌿 Verde Wellness API Testing Suite")
    print("=" * 50)
    
    tester = VerdeWellnessAPITester()
    
    # Test sequence
    print("\n📋 Running Backend API Tests...")
    
    # 1. Test root endpoint
    tester.test_root_endpoint()
    
    # 2. Test services endpoint
    services_success, services = tester.test_get_services()
    
    # 3. Test availability endpoint
    tester.test_get_availability()
    
    # 4. Test booking creation
    if services_success:
        booking_success = tester.test_create_booking(services)
        
        # 5. Test getting all bookings
        if booking_success:
            tester.test_get_bookings()
            
            # 6. Test getting specific booking
            tester.test_get_specific_booking()
            
            # 7. Test availability after booking
            tester.test_availability_after_booking()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All backend tests passed!")
        return 0
    else:
        print("❌ Some backend tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())