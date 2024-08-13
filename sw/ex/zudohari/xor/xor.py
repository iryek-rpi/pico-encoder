def create_token(string):
    # 문자열의 각 문자의 ASCII 값을 더함
    ascii_sum = sum(ord(char) for char in string)
    # 1바이트 값으로 변환 (0-255 사이 값)
    token = ascii_sum % 256
    return token

def xor_with_token(string, token):
    # 각 문자를 토큰 값으로 XOR 연산 수행
    xor_result = [ord(char) ^ token for char in string]
    return xor_result

def ascii_to_string(ascii_list):
    # ASCII 값 리스트를 문자열로 변환
    return ''.join(chr(val) for val in ascii_list)

# 패스워드를 이용해 토큰 생성
password = "password"
token = create_token(password)

# 첫 번째 XOR 연산(encode)
original_string ="This is a my data"
xor_result = xor_with_token(original_string, token)
xor_result_str = ascii_to_string(xor_result)
print(f"Original string: '{original_string}'")
print(f"Token: {token}")
print(f"XOR result (ASCII values): {xor_result}")
print(f"XOR result (as string): '{xor_result_str}'")

# 두 번째 XOR 연산 (decode)
restored_result = xor_with_token(xor_result_str, token)
restored_string = ascii_to_string(restored_result)
print(f"Restored string: '{restored_string}'") 
