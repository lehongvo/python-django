"""
Python Fundamentals Review
This file covers the basics of Python programming
"""

# ============================================
# 1. Variables and Data Types
# ============================================

# Numbers
age = 25
price = 19.99
rating = 4.5

# Strings
name = "Alice"
message = 'Hello World'
multiline = """This is a
multiline string"""

# Boolean
is_active = True
is_admin = False

# Lists - ordered, mutable collection
fruits = ["apple", "banana", "orange"]
numbers = [1, 2, 3, 4, 5]

# Tuples - ordered, immutable collection
coordinates = (10, 20)
status = ("active", "verified")

# Dictionaries - key-value pairs
student = {
    "name": "Alice",
    "age": 20,
    "major": "Computer Science"
}

# Sets - unordered collection of unique items
unique_numbers = {1, 2, 3, 4, 5}
unique_colors = {"red", "green", "blue"}

# ============================================
# 2. Functions
# ============================================

# Simple function
def greet(name):
    """Function to greet a person"""
    return f"Hello, {name}!"

# Function with default parameters
def greet_with_default(name, greeting="Hello"):
    """Function with default parameter"""
    return f"{greeting}, {name}!"

# Function with multiple parameters
def calculate_area(length, width):
    """Calculate area of a rectangle"""
    return length * width

# Lambda function
multiply = lambda x, y: x * y

# Function with docstring
def add_numbers(a, b):
    """
    Add two numbers together.
    
    Args:
        a (int): First number
        b (int): Second number
    
    Returns:
        int: Sum of a and b
    """
    return a + b


# ============================================
# 3. Classes and Objects
# ============================================

class Person:
    """A class representing a person"""
    
    # Class attribute
    species = "Homo sapiens"
    
    def __init__(self, name, age):
        """Initialize a Person instance"""
        self.name = name
        self.age = age
    
    def introduce(self):
        """Person introduces themselves"""
        return f"Hi, I'm {self.name} and I'm {self.age} years old"
    
    def have_birthday(self):
        """Increase age by 1"""
        self.age += 1
        return self.age


class Student(Person):
    """A class representing a student, inheriting from Person"""
    
    def __init__(self, name, age, major):
        """Initialize a Student instance"""
        super().__init__(name, age)
        self.major = major
        self.grades = []
    
    def add_grade(self, grade):
        """Add a grade to student's record"""
        self.grades.append(grade)
    
    def get_average(self):
        """Calculate average grade"""
        if not self.grades:
            return 0
        return sum(self.grades) / len(self.grades)


# ============================================
# 4. Modules
# ============================================

# Importing standard library modules
import os
import sys
from datetime import datetime

# Importing specific functions
from math import sqrt, pi

# Example: Creating a simple module
def get_current_time():
    """Get current time as string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================================
# 5. List Comprehensions
# ============================================

# Traditional way
squares = []
for x in range(10):
    squares.append(x ** 2)

# Pythonic way
squares = [x ** 2 for x in range(10)]

# With condition
even_squares = [x ** 2 for x in range(10) if x % 2 == 0]


# ============================================
# 6. Error Handling
# ============================================

def divide_numbers(a, b):
    """Safely divide two numbers"""
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        return "Cannot divide by zero"
    except TypeError:
        return "Invalid input types"
    finally:
        print("Division operation completed")


# ============================================
# 7. File Operations
# ============================================

def read_file_example(filename):
    """Read content from a file"""
    try:
        with open(filename, 'r') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        return "File not found"


def write_file_example(filename, content):
    """Write content to a file"""
    with open(filename, 'w') as file:
        file.write(content)


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    # Using Person class
    person1 = Person("Alice", 30)
    print(person1.introduce())
    
    # Using Student class
    student1 = Student("Bob", 20, "Computer Science")
    student1.add_grade(85)
    student1.add_grade(90)
    print(f"Average grade: {student1.get_average()}")
    
    # Using functions
    print(greet("World"))
    print(calculate_area(5, 10))
    
    # List comprehension
    print(f"Squares: {[x**2 for x in range(5)]}")

