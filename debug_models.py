"""
Debug script to test all API endpoints
Tests authentication, prediction, similarity, and history endpoints
"""

import requests
import json
import os
from pathlib import Path
import base64
from PIL import Image
import io

# Configuration
BASE_URL = "http://127.0.0.1:8000"  # Change if your server runs on different port
BASE_DIR = Path(__file__).resolve().parent

"""
Debug script to test all API endpoints
Tests authentication, prediction, similarity, and history endpoints
"""

import requests
import json
import os
from pathlib import Path
import base64
from PIL import Image
import io


# Configuration
BASE_URL = "http://127.0.0.1:8000"  # Change if your server runs on different port
BASE_DIR = Path(__file__).resolve().parent

# Test credentials
TEST_USER = {
	"username": "test_user_debug",
	"email": "debug@test.com",
	"password": "TestPass123!",
	"password2": "TestPass123!"
}

# Global token storage
ACCESS_TOKEN = None
REFRESH_TOKEN = None


def print_header(title):
	"""Print formatted section header"""
	print("\n" + "="*70)
	print(f" {title}")
	print("="*70)


def print_response(response, show_full=False):
	"""Print formatted API response"""
	print(f"\nStatus Code: {response.status_code}")
	try:
		data = response.json()
		if show_full:
			print(f"Response:\n{json.dumps(data, indent=2)}")
		else:
			# Show limited response
			if isinstance(data, dict):
				for key, value in data.items():
					if key in ['reference_image', 'user_image', 'blended_overlay'] and isinstance(value, str) and len(value) > 100:
						print(f"  {key}: [base64 image data, {len(value)} chars]")
					elif isinstance(value, str) and len(value) > 200:
						print(f"  {key}: {value[:200]}...")
					else:
						print(f"  {key}: {value}")
			else:
				print(f"Response: {data}")
	except:
		print(f"Response (text): {response.text[:500]}")


def test_signup():
	"""Test 1: Signup endpoint"""
	print_header("TEST 1: SIGNUP - POST /api/signup/")
	
	url = f"{BASE_URL}/api/signup/"
	response = requests.post(url, json=TEST_USER)
	print_response(response)
	
	if response.status_code == 201:
		print("✓ Signup successful!")
		return True
	elif response.status_code == 400 and 'username' in response.text:
		print("⚠ User already exists (this is okay for testing)")
		return True
	else:
		print("✗ Signup failed!")
		return False


def test_signin():
	"""Test 2: Signin endpoint"""
	global ACCESS_TOKEN, REFRESH_TOKEN
	
	print_header("TEST 2: SIGNIN - POST /api/signin/")
	
	url = f"{BASE_URL}/api/signin/"
	credentials = {
		"username": TEST_USER["username"],
		"password": TEST_USER["password"]
	}
	
	response = requests.post(url, json=credentials)
	print_response(response)
	
	if response.status_code == 200:
		data = response.json()
		ACCESS_TOKEN = data.get('access')
		REFRESH_TOKEN = data.get('refresh')
		print(f"\n✓ Signin successful!")
		print(f"  Access Token: {ACCESS_TOKEN[:50]}...")
		return True
	else:
		print("✗ Signin failed!")
		return False


def test_change_password():
	"""Test 3: Change password endpoint"""
	print_header("TEST 3: CHANGE PASSWORD - POST /api/change-password/")
	
	url = f"{BASE_URL}/api/change-password/"
	headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
	data = {
		"old_password": TEST_USER["password"],
		"new_password": "NewTestPass123!"
	}
	
	response = requests.post(url, json=data, headers=headers)
	print_response(response)
	
	if response.status_code == 200:
		print("✓ Password changed!")
		# Change it back
		data_revert = {
			"old_password": "NewTestPass123!",
			"new_password": TEST_USER["password"]
		}
		requests.post(url, json=data_revert, headers=headers)
		print("  (Password reverted back for further testing)")
		return True
	else:
		print("✗ Password change failed!")
		return False


def test_change_username():
	"""Test 4: Change username endpoint"""
	print_header("TEST 4: CHANGE USERNAME - POST /api/change-username/")
	
	url = f"{BASE_URL}/api/change-username/"
	headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
	data = {
		"new_username": "test_user_debug_new"
	}
	
	response = requests.post(url, json=data, headers=headers)
	print_response(response)
	
	if response.status_code == 200:
		print("✓ Username changed!")
		# Change it back
		data_revert = {
			"new_username": TEST_USER["username"]
		}
		requests.post(url, json=data_revert, headers=headers)
		print("  (Username reverted back for further testing)")
		return True
	else:
		print("✗ Username change failed!")
		return False


def test_predict():
	"""Test 5: Prediction endpoint"""
	print_header("TEST 5: PREDICT - POST /api/predict/")
	
	# Use a reference image for testing
	test_image_path = BASE_DIR / "api" / "reference_images" / "class_2.png"
	
	if not test_image_path.exists():
		print(f"✗ Test image not found: {test_image_path}")
		return False
	
	url = f"{BASE_URL}/api/predict/"
	headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
	
	with open(test_image_path, 'rb') as f:
		files = {'image': ('test.png', f, 'image/png')}
		response = requests.post(url, files=files, headers=headers)
	
	print(f"Test Image: {test_image_path}")
	print_response(response)
	
	if response.status_code == 200:
		print("✓ Prediction successful!")
		return True
	else:
		print("✗ Prediction failed!")
		return False


def test_similarity():
	"""Test 6: Similarity endpoint"""
	print_header("TEST 6: SIMILARITY - POST /api/similarity/")
	
	# Use a reference image for testing (class 12, within 0-35 range)
	test_image_path = BASE_DIR / "api" / "reference_images" / "class_2.png"
	
	if not test_image_path.exists():
		print(f"✗ Test image not found: {test_image_path}")
		return False
	
	url = f"{BASE_URL}/api/similarity/"
	headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
	
	with open(test_image_path, 'rb') as f:
		files = {'image': ('test.png', f, 'image/png')}
		data = {'target_class': '12'}  # Class 12 is within 0-35 range
		response = requests.post(url, files=files, data=data, headers=headers)
	
	print(f"Test Image: {test_image_path}")
	print(f"Target Class: 12 (valid range: 0-35)")
	print_response(response, show_full=False)
	
	if response.status_code == 200:
		print("✓ Similarity check successful!")
		
		# Save all three images if present
		try:
			result = response.json()
			comparison_dir = BASE_DIR / "comparison"
			comparison_dir.mkdir(exist_ok=True)
			
			# Save reference image
			if 'reference_image' in result:
				reference_data = result['reference_image']
				if reference_data.startswith('data:image/png;base64,'):
					base64_data = reference_data.split(',')[1]
					image_data = base64.b64decode(base64_data)
					output_path = comparison_dir / "api_test_reference.png"
					with open(output_path, 'wb') as f:
						f.write(image_data)
					print(f"  → Reference image saved: {output_path}")
			
			# Save user image
			if 'user_image' in result:
				user_data = result['user_image']
				if user_data.startswith('data:image/png;base64,'):
					base64_data = user_data.split(',')[1]
					image_data = base64.b64decode(base64_data)
					output_path = comparison_dir / "api_test_user.png"
					with open(output_path, 'wb') as f:
						f.write(image_data)
					print(f"  → User image saved: {output_path}")
			
			# Save blended overlay
			if 'blended_overlay' in result:
				blended_data = result['blended_overlay']
				if blended_data.startswith('data:image/png;base64,'):
					base64_data = blended_data.split(',')[1]
					image_data = base64.b64decode(base64_data)
					output_path = comparison_dir / "api_test_blended.png"
					with open(output_path, 'wb') as f:
						f.write(image_data)
					print(f"  → Blended overlay saved: {output_path}")
					
		except Exception as e:
			print(f"  ⚠ Could not save images: {e}")
		
		return True
	else:
		print("✗ Similarity check failed!")
		return False


def test_prediction_history():
	"""Test 7: Get prediction history"""
	print_header("TEST 7: PREDICTION HISTORY - GET /api/history/predictions/")
	
	url = f"{BASE_URL}/api/history/predictions/"
	headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
	
	response = requests.get(url, headers=headers)
	print_response(response, show_full=True)
	
	if response.status_code == 200:
		data = response.json()
		print(f"\n✓ Retrieved {data.get('count', 0)} prediction history records")
		return True
	else:
		print("✗ Failed to get prediction history!")
		return False


def test_similarity_history():
	"""Test 8: Get similarity history"""
	print_header("TEST 8: SIMILARITY HISTORY - GET /api/history/similarities/")
	
	url = f"{BASE_URL}/api/history/similarities/"
	headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
	
	response = requests.get(url, headers=headers)
	print_response(response, show_full=True)
	
	if response.status_code == 200:
		data = response.json()
		print(f"\n✓ Retrieved {data.get('count', 0)} similarity history records")
		return True
	else:
		print("✗ Failed to get similarity history!")
		return False


def test_unauthorized_access():
	"""Test 9: Test unauthorized access"""
	print_header("TEST 9: UNAUTHORIZED ACCESS - Without Token")
	
	url = f"{BASE_URL}/api/predict/"
	test_image_path = BASE_DIR / "api" / "reference_images" / "class_0.png"
	
	if test_image_path.exists():
		with open(test_image_path, 'rb') as f:
			files = {'image': ('test.png', f, 'image/png')}
			response = requests.post(url, files=files)
		
		print_response(response)
		
		if response.status_code == 401:
			print("✓ Correctly rejected unauthorized request!")
			return True
		else:
			print("✗ Should have rejected unauthorized request!")
			return False
	else:
		print("⚠ Skipping test - no test image available")
		return True


def main():
	"""Run all endpoint tests"""
	print("\n" + "="*70)
	print(" "*20 + "API ENDPOINT TESTER")
	print("="*70)
	print(f"\nBase URL: {BASE_URL}")
	print(f"Make sure your Django server is running!")
	print("\nStarting tests in 3 seconds...")
	
	import time
	time.sleep(3)
	
	results = {}
	
	# Run tests
	results['Signup'] = test_signup()
	results['Signin'] = test_signin()
	
	if not ACCESS_TOKEN:
		print("\n✗ Cannot continue without access token!")
		return
	
	results['Change Password'] = test_change_password()
	results['Change Username'] = test_change_username()
	results['Predict'] = test_predict()
	results['Similarity'] = test_similarity()
	results['Prediction History'] = test_prediction_history()
	results['Similarity History'] = test_similarity_history()
	results['Unauthorized Access'] = test_unauthorized_access()
	
	# Summary
	print_header("TEST SUMMARY")
	passed = sum(1 for v in results.values() if v)
	total = len(results)
	
	print(f"\nResults: {passed}/{total} tests passed\n")
	
	for test_name, result in results.items():
		status = "✓ PASS" if result else "✗ FAIL"
		print(f"  {status} - {test_name}")
	
	print("\n" + "="*70)
	
	if passed == total:
		print("🎉 ALL TESTS PASSED! Your API is working correctly.")
	else:
		print(f"⚠ {total - passed} test(s) failed. Check the output above for details.")
	
	print("="*70 + "\n")


if __name__ == '__main__':
	try:
		main()
	except requests.exceptions.ConnectionError:
		print("\n✗ ERROR: Could not connect to the server!")
		print(f"Make sure Django is running at {BASE_URL}")
		print("\nStart the server with: python manage.py runserver")
	except KeyboardInterrupt:
		print("\n\n⚠ Tests interrupted by user.")
	except Exception as e:
		print(f"\n✗ ERROR: {e}")
		import traceback
		traceback.print_exc()
