#!/usr/bin/env python3
"""
Prime number generator for numbers between 11 and 71 inclusive.

This script generates and outputs a list of prime numbers in the range [11, 71].
"""

def is_prime(n: int) -> bool:
    """
    Check if a number is prime.
    
    Args:
        n: Integer to check for primality
        
    Returns:
        True if n is prime, False otherwise
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Only check odd divisors up to sqrt(n)
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

def get_primes_in_range(start: int, end: int) -> list[int]:
    """
    Get all prime numbers in a given range (inclusive).
    
    Args:
        start: Start of range (inclusive)
        end: End of range (inclusive)
        
    Returns:
        List of prime numbers in the range
    """
    return [n for n in range(start, end + 1) if is_prime(n)]

def main() -> None:
    """Main function to output prime numbers between 11 and 71."""
    primes = get_primes_in_range(11, 71)
    print(primes)

if __name__ == "__main__":
    main()