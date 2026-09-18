year = 2024
if year % 4 == 0:
    print("Leap Year")
else:
    print("Not Leap Year")


n = 123
total = 0
for digit in str(n):
    total += int(digit)

print(total)

nums = [10, 20, 30, 40]
total = 0
for n in nums:
    total += n
print(total)    