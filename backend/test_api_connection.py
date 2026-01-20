"""
Test script to verify the new API provider connection.
"""
import asyncio
from app.core.openai_client import openai_client
from app.config import settings


async def test_chat_completion():
    """Test basic chat completion"""
    print(f"Testing API connection...")
    print(f"Base URL: {settings.OPENAI_BASE_URL}")
    print(f"Model: {settings.OPENAI_MODEL}")
    print()
    
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello! API is working correctly.' in one sentence."}
        ]
        
        print("Sending test request...")
        response = await openai_client.chat_completion(messages=messages)
        
        print("✓ Success!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
        return False


async def test_vision_completion():
    """Test vision API (if supported)"""
    print("\nTesting vision API...")
    
    try:
        # Simple test image URL (1x1 red pixel)
        test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
        
        response = await openai_client.vision_completion(
            image_url=test_image,
            prompt="Describe this image in one word."
        )
        
        print("✓ Success!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"✗ Vision API Error: {type(e).__name__}: {str(e)}")
        print("Note: Vision API may not be supported by this model.")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("API Provider Connection Test")
    print("=" * 60)
    print()
    
    chat_ok = await test_chat_completion()
    vision_ok = await test_vision_completion()
    
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Chat API: {'✓ PASS' if chat_ok else '✗ FAIL'}")
    print(f"Vision API: {'✓ PASS' if vision_ok else '✗ FAIL (may not be supported)'}")
    print()
    
    if chat_ok:
        print("✓ The API provider is configured correctly!")
    else:
        print("✗ Please check your API key and configuration.")


if __name__ == "__main__":
    asyncio.run(main())
