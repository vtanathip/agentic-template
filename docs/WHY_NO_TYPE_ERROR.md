# Why Python Doesn't Catch Method Errors Before Runtime

## The Problem

You asked: **"When it doesn't have the method name `get_stats()`, why doesn't it throw a type error before runtime?"**

This is an excellent question that highlights a fundamental difference between Python and statically-typed languages!

## The Answer: Dynamic vs Static Typing

### Python is **Dynamically Typed**

```python
# This code compiles successfully even though get_stats() doesn't exist!
def get_collection_stats(self):
    stats = self.collection.get_stats()  # ❌ No error until execution
    return stats
```

**What happens:**
1. ✅ Python parses the file (syntax check)
2. ✅ Function is defined successfully  
3. ✅ Code runs... until it hits this line
4. ❌ **Runtime Error**: `AttributeError: 'Collection' object has no attribute 'get_stats'`

### Statically-Typed Languages (Java, TypeScript, C++)

```typescript
// TypeScript - Error at COMPILE TIME
interface Collection {
    num_entities: number;
    // get_stats() doesn't exist in the interface
}

collection.get_stats();  // ❌ COMPILE ERROR immediately
// Error: Property 'get_stats' does not exist on type 'Collection'
```

## How to Catch These Errors BEFORE Runtime in Python

### Option 1: Use Static Type Checkers (Recommended)

Install and use tools like **mypy** or **pyright** (VS Code's Pylance):

```bash
# Install mypy
uv add --dev mypy types-requests

# Run type checking
uv run mypy src/
```

**Example with proper type hints:**

```python
from typing import Optional
from pymilvus import Collection

class MilvusVectorStore:
    def __init__(self):
        self.collection: Optional[Collection] = None
    
    def get_collection_stats(self) -> Dict[str, Any]:
        if not self.collection:
            raise RuntimeError("Must connect first")
        
        # mypy would catch this error!
        stats = self.collection.get_stats()  # ❌ mypy error: No attribute 'get_stats'
        
        # Correct way
        row_count = self.collection.num_entities  # ✅ mypy knows this exists
        return {"row_count": row_count}
```

### Option 2: Use IDE with Type Checking (VS Code + Pylance)

VS Code with Pylance (Python extension) provides real-time type checking:

1. Install Python extension
2. Set type checking mode in settings:
   ```json
   {
     "python.analysis.typeCheckingMode": "basic"  // or "strict"
   }
   ```
3. See errors immediately in the editor! 🎉

### Option 3: Add Runtime Checks

```python
def get_collection_stats(self) -> Dict[str, Any]:
    if not self.collection:
        raise RuntimeError("Must connect first")
    
    # Check if method exists before calling
    if not hasattr(self.collection, 'num_entities'):
        raise AttributeError("Collection doesn't have num_entities")
    
    return {"row_count": self.collection.num_entities}
```

### Option 4: Use Protocol/ABC for Better Type Safety

```python
from typing import Protocol

class CollectionProtocol(Protocol):
    """Define what methods we expect on Collection."""
    num_entities: int
    
    def insert(self, data: list) -> None: ...
    def search(self, vectors: list) -> list: ...

class MilvusVectorStore:
    def __init__(self):
        self.collection: Optional[CollectionProtocol] = None
```

## Why Python Is This Way

### Advantages of Dynamic Typing:
- ✅ **Flexibility** - Duck typing ("if it walks like a duck...")
- ✅ **Rapid prototyping** - Less boilerplate
- ✅ **Easier to learn** - No complex type system
- ✅ **Meta-programming** - Can modify objects at runtime

### Disadvantages:
- ❌ **Runtime errors** - Typos only found when code runs
- ❌ **Less IDE help** - Harder for autocomplete to know what exists
- ❌ **Refactoring risks** - Renaming methods might miss usages

## Best Practices for Your Project

1. **Add mypy to your CI/CD**:
   ```yaml
   # In GitHub Actions or similar
   - run: uv run mypy src/ --strict
   ```

2. **Enable type checking in VS Code**:
   - Already configured with Pylance! Just increase strictness.

3. **Add type hints to new code**:
   ```python
   def get_stats(self) -> Dict[str, Any]:  # Always specify return type
       ...
   ```

4. **Write integration tests** (like you did!):
   - Tests catch runtime errors early
   - Your PDF upload tests caught the `get_stats()` bug! ✅

## Summary

| Language Type | Error Detection | Example |
|--------------|----------------|---------|
| **Static** (Java, TypeScript) | Compile time | ✅ Catches before running |
| **Dynamic** (Python) | Runtime | ❌ Only finds errors when executing |
| **Python + mypy** | Static analysis | ✅ Can catch before running |

**Answer to your question:** Python doesn't throw errors before runtime because it's dynamically typed - it doesn't check if methods exist until the code actually tries to call them. Use mypy or Pylance to get static type checking!
