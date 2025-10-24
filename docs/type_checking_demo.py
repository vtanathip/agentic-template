"""
Demonstration: Why Python doesn't catch method errors before runtime.

Run this file to see the difference between runtime errors and type checking.
"""

# Example 1: This code will RUN but fail at runtime
class MyClass:
    def existing_method(self):
        return "I exist!"
    
def will_fail_at_runtime():
    obj = MyClass()
    # Python doesn't check if this method exists until you call it!
    result = obj.non_existent_method()  # ❌ No error until this line runs
    return result

# Example 2: With type hints, mypy can catch this
from typing import Protocol

class MyProtocol(Protocol):
    """Define expected methods."""
    def existing_method(self) -> str: ...

def typed_function(obj: MyProtocol) -> str:
    # If you run: mypy this_file.py
    # It will warn about this line!
    return obj.non_existent_method()  # ❌ mypy would catch this

# Example 3: The actual bug from your code
class FakeCollection:
    """Simulates Milvus Collection without get_stats()."""
    def __init__(self):
        self.num_entities = 42  # ✅ This exists
    
    # Note: get_stats() is NOT defined

class VectorStore:
    def __init__(self):
        self.collection = FakeCollection()
    
    def broken_get_stats(self):
        """This is what your code was trying to do."""
        # Python compiles this fine, but fails at runtime!
        stats = self.collection.get_stats()  # ❌ AttributeError at runtime
        return {"row_count": stats["row_count"]}
    
    def fixed_get_stats(self):
        """This is the fix."""
        # Use the method that actually exists
        row_count = self.collection.num_entities  # ✅ Works!
        return {"row_count": row_count}


if __name__ == "__main__":
    print("=" * 60)
    print("Python Dynamic Typing Demonstration")
    print("=" * 60)
    
    # Test 1: Runtime error
    print("\n1. Testing method that doesn't exist...")
    try:
        will_fail_at_runtime()
    except AttributeError as e:
        print(f"   ❌ Runtime Error: {e}")
        print("   → Python only discovered the error when trying to call it!")
    
    # Test 2: The actual bug
    print("\n2. Testing the get_stats() bug...")
    store = VectorStore()
    try:
        store.broken_get_stats()
    except AttributeError as e:
        print(f"   ❌ Runtime Error: {e}")
        print("   → 'Collection' object has no attribute 'get_stats'")
    
    # Test 3: The fix
    print("\n3. Testing the fixed version...")
    try:
        result = store.fixed_get_stats()
        print(f"   ✅ Success: {result}")
        print("   → Using num_entities instead of get_stats()")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("KEY TAKEAWAY:")
    print("=" * 60)
    print("Python is DYNAMICALLY typed:")
    print("  - ✅ Fast to write code")
    print("  - ❌ Errors only found at runtime")
    print("\nTo catch errors earlier:")
    print("  1. Use mypy: uv run mypy src/")
    print("  2. Use VS Code + Pylance with type checking")
    print("  3. Write tests (like you did!)")
    print("=" * 60)
