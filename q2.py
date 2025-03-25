s = input("Enter a string: ")

def custom_sort(char):
    if char.islower():
        return (char, 0)
    else:
        return (char.lower(), 1)

s = sorted(s, key=custom_sort)

result = ''.join(s)
print(result)

# s = input("Enter a string: ")
# print(f"Input string: {s}")

# def custom_sort(char):
#     if char.islower():
#         result = (char, 0)
#         print(f"Character '{char}' is lowercase, sort key: {result}")
#         return result
#     else:
#         result = (char.lower(), 1)
#         print(f"Character '{char}' is uppercase, sort key: {result}")
#         return result

# s = sorted(s, key=custom_sort)
# print(f"Sorted list: {s}")

# result = ''.join(s)
# print(f"Final result: {result}")

# //////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////

s = input("Enter a string: ")

s = sorted(s, key=lambda c: (c.lower(), c.isupper()))

result = ''.join(s)
print(result)

# s = input("Enter a string: ")

# def custom_sort_lambda(c):
#     result = (c.lower(), c.isupper())
#     print(f"Character '{c}', sort key: {result}")
#     return result

# s = sorted(s, key=custom_sort_lambda)
# print(f"Sorted list: {s}")

# result = ''.join(s)
# print(f"Final result: {result}")


# //////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////

# Bubble sort
s = input("Enter a string: ")
print(f"Input string: {s}")

char_list = list(s)

n = len(char_list)
for i in range(n):
    for j in range(0, n - i - 1):
        a, b = char_list[j], char_list[j + 1]
        if (a.lower() > b.lower()) or (a.lower() == b.lower() and a.isupper() and b.islower()):
            char_list[j], char_list[j + 1] = char_list[j + 1], char_list[j]
            print(f"Swapped '{a}' with '{b}': {''.join(char_list)}")

result = ''.join(char_list)
print(f"Final result: {result}")

# //////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////

# Insertion sort
s = input("Enter a string: ")

char_list = list(s)

n = len(char_list)

for i in range(1, n):
    key = char_list[i]
    j = i - 1
    while j >= 0 and ((char_list[j].lower() > key.lower()) or 
                      (char_list[j].lower() == key.lower() and char_list[j].isupper() and key.islower())):
        char_list[j + 1] = char_list[j]
        j -= 1
    char_list[j + 1] = key
    print(f"Inserted '{key}' at position {j + 1}: {''.join(char_list)}")

result = ''.join(char_list)
print(f"Final result: {result}")

# //////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////

# Selection sort
s = input("Enter a string: ")

char_list = list(s)

n = len(char_list)

for i in range(n):
    min_index = i
    for j in range(i + 1, n):
        a, b = char_list[min_index], char_list[j]
        if (a.lower() > b.lower()) or (a.lower() == b.lower() and a.isupper() and b.islower()):
            min_index = j
    char_list[i], char_list[min_index] = char_list[min_index], char_list[i]
    print(f"Swapped '{char_list[i]}' with '{char_list[min_index]}': {''.join(char_list)}")

result = ''.join(char_list)
print(f"Final result: {result}")

# //////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////

# Merge sort

def merge_sort(char_list):
    if len(char_list) > 1:
        mid = len(char_list) // 2
        left_half = char_list[:mid]
        right_half = char_list[mid:]

        merge_sort(left_half)
        merge_sort(right_half)

        i = j = k = 0

        while i < len(left_half) and j < len(right_half):
            a, b = left_half[i], right_half[j]
            if (a.lower() < b.lower()) or (a.lower() == b.lower() and a.islower()):
                char_list[k] = left_half[i]
                i += 1
            else:
                char_list[k] = right_half[j]
                j += 1
            k += 1

        while i < len(left_half):
            char_list[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            char_list[k] = right_half[j]
            j += 1
            k += 1

s = input("Enter a string: ")
char_list = list(s)
print(f"Input string: {s}")

merge_sort(char_list)

result = ''.join(char_list)
print(f"Final result: {result}")

# //////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////
# Quick sort

def partition(char_list, low, high):
    i = low - 1
    pivot = char_list[high]

    for j in range(low, high):
        a, b = char_list[j], pivot
        if (a.lower() < b.lower()) or (a.lower() == b.lower() and a.islower()):
            i += 1
            char_list[i], char_list[j] = char_list[j], char_list[i]

    char_list[i + 1], char_list[high] = char_list[high], char_list[i + 1]
    return i + 1

def quick_sort(char_list, low, high):
    if low < high:
        pi = partition(char_list, low, high)
        quick_sort(char_list, low, pi - 1)
        quick_sort(char_list, pi + 1, high)

s = input("Enter a string: ")
char_list = list(s)
print(f"Input string: {s}")
n = len(char_list)

quick_sort(char_list, 0, n - 1)

result = ''.join(char_list)
print(f"Final result: {result}")
