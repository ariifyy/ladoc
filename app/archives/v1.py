import hashlib
import requests



# Hash the password using SHA1
password = input("Enter the password to check: ")
str(password)
sha1_hashed = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()

# Use the first 5 characters of the hash
prefix = sha1_hashed[:5]
suffix = sha1_hashed[5:]

# API URL
url = f"https://api.pwnedpasswords.com/range/{prefix}"

# Make the request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Check if the suffix is in the response
    hashes = response.text.splitlines()
    found = any(suffix in line.split(':')[0] for line in hashes)
    if found:
        print("The password has been compromised!")
    else:
        print("The password is safe (not found in the database).")
else:
    print(f"Failed to fetch data from API. Status code: {response.status_code}")

print(prefix, suffix)