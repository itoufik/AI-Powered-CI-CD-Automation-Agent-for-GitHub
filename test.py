def fibonacci(n):
    """Generate the first n Fibonacci numbers."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    fib_sequence = [0, 1]
    for i in range(2, n):
        fib_sequence.append(fib_sequence[i-1] + fib_sequence[i-2])
    
    return fib_sequence


def fibonacci_nth(n):
    """Return the nth Fibonacci number (0-indexed)."""
    if n < 0:
        return None
    elif n == 0:
        return 0
    elif n == 1:
        return 1
    
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    
    return curr


# Example usage
if __name__ == "__main__":
    # Generate first 10 Fibonacci numbers
    print("First 10 Fibonacci numbers:")
    print(fibonacci(10))
    
    # Get the 15th Fibonacci number
    print("\nThe 15th Fibonacci number (0-indexed):")
    print(fibonacci_nth(15))
    
    # Generate more numbers
    print("\nFirst 20 Fibonacci numbers:")
    print(fibonacci(20))