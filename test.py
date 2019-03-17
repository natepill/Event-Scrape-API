letters = ['a', 'b', 'c', 'd']
numbers = [1,2,34,5,6,6]

zipped_object = zip(letters, numbers)

# print(list(zipped_object))

for pair in zipped_object:
    print(pair)
