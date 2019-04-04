# This is a very simple example to help understand how PoW works.

# Let’s decide that the hash of some integer x multiplied by another y must end in 0. So, hash(x * y) = ac23dc...0.
# And for this simplified example, let’s fix x = 5

# Note: We will use the SHA-256 hash to generate cryptographic keys on our strings.

from hashlib import sha256

x = 5
y = 0  # We don't know what y should be yet.

while sha256(f'{x*y}'.encode()).hexdigest()[-1] != "0":
    y += 1

key = sha256(f'{x*y}'.encode()).hexdigest()

print(f'The solution is y = {y}')
print(f'hash(5 * {y}) = {key}')
