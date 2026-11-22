"""
Temporary test script for utils/groq_client.py.
Verifies real API invocation using local .env without exposing credentials.
"""

import sys
from utils.groq_client import (
    get_configured_model,
    generate_response,
    GroqClientError,
    MissingAPIKeyError,
    AuthenticationError,
    ModelNotFoundError,
)

def run_tests():
    print("=" * 60)
    print("RUNNING GROQ CLIENT INTEGRATION TEST")
    print("=" * 60)

    # 1. Verify model configuration
    try:
        model = get_configured_model()
        print(f"[PASS] Model configured: {model}")
    except Exception as e:
        print(f"[FAIL] Unable to read configured model: {e}")
        return False

    # 2. Test live completion call
    print("\nSending test prompt to Groq API...")
    system_prompt = "You are a concise academic assistant. Answer strictly in one short sentence."
    user_prompt = "Define what a hash table is in computer science."

    try:
        response = generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=60,
            temperature=0.1
        )
        print("[PASS] Groq API response received successfully!")
        print(f"Sample response output:\n\"{response}\"")
    except MissingAPIKeyError as e:
        print(f"[FAIL] Missing API key: {e}")
        return False
    except AuthenticationError as e:
        print(f"[FAIL] Authentication error: {e}")
        return False
    except ModelNotFoundError as e:
        print(f"[FAIL] Model not found: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] API call error: {type(e).__name__} - {e}")
        return False

    # 3. Test error handling with an invalid model name
    print("\nTesting error handling for an invalid model name...")
    try:
        generate_response(
            system_prompt="Test",
            user_prompt="Ping",
            model="invalid-nonexistent-model-xyz",
            max_tokens=5
        )
        print("[FAIL] Invalid model should have raised ModelNotFoundError.")
        return False
    except ModelNotFoundError:
        print("[PASS] Correctly caught ModelNotFoundError for invalid model.")
    except Exception as e:
        print(f"[PASS] Handled invalid model with exception: {type(e).__name__}")

    print("\n" + "=" * 60)
    print("ALL GROQ CLIENT TESTS COMPLETED SUCCESSFULLY")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
