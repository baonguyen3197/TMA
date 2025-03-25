s = input("Enter a string: ")

s = list(s)

s.reverse()

s.append(s.pop(0))

result = ''.join(s)

print(result)

# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////

s = input("Enter a string: ")

char_list = list(s)
print(f"{char_list}")

n = len(char_list)
print(f"Number of characters: {n}")

for i in range(n // 2):
    print(f"Swap characters at positions {i}:{char_list[i]} and {n - i - 1}:{char_list[n - i - 1]}")
    char_list[i], char_list[n - i - 1] = char_list[n - i - 1], char_list[i]

first_char = char_list[0]
print(f"First character: {first_char}")
for i in range(1, n):
    char_list[i - 1] = char_list[i]
    print(f"Shifted '{char_list[i]}' to position {i - 1}: {''.join(char_list)}")
char_list[-1] = first_char
print(f"characters: {char_list[-1]}")
print(f"Shifted '{first_char}' to position {n - 1}: {''.join(char_list)}")

result = ''.join(char_list)

print(result)

# /////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////
