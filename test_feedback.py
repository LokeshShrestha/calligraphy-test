"""
Test script for FeedbackView endpoint
Usage: python test_feedback.py <path_to_image>
"""
import requests
import sys
import os

def test_feedback_endpoint(image_path, base_url="http://127.0.0.1:8000"):
    """
    Test the feedback endpoint with an image
    
    Args:
        image_path: Path to the image file to send
        base_url: Base URL of the Django server (default: http://127.0.0.1:8000)
    """
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found at {image_path}")
        return
    
    endpoint = f"{base_url}/api/feedback/"
    
    print(f"🔄 Testing Feedback API...")
    print(f"📤 Sending image: {image_path}")
    print(f"🌐 Endpoint: {endpoint}")
    print("-" * 60)
    
    try:
        # Open and send the image file
        with open(image_path, 'rb') as img_file:
            files = {'image': img_file}
            response = requests.post(endpoint, files=files)
        
        # Print status code
        print(f"\n📊 Status Code: {response.status_code}")
        
        # Parse and display response
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS!")
            print("-" * 60)
            print("📝 Feedback from Gemini:")
            print("-" * 60)
            print(data.get('feedback', 'No feedback received'))
            print("-" * 60)
        else:
            print(f"\n❌ ERROR: Request failed")
            print("Response:")
            try:
                print(response.json())
            except:
                print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print("Make sure the Django server is running:")
        print("  python manage.py runserver")
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_feedback.py <path_to_image>")
        print("\nExample:")
        print("  python test_feedback.py test_img/sample.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    test_feedback_endpoint(image_path)
