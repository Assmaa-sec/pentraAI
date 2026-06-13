#!/usr/bin/env python3
from math import gcd, lcm
from sympy import primerange
from binascii import unhexlify

n = int('b03ea698ce2b51fb00e11e6fbaf1e5373dc5b0c70eb2b14a36d21e8667be8774eee51f6050a10237f6b24f21204fc8013681e7ed72ed051188f3274aae8f1de0d39389b514c196fa82c98a270bfabefd044da8c687b0e114ebbde82536c0709ac5ad81bfe0077e9d9b798ad5abecee52767e68f8060c45936521fd93893102eb1676f2ff41324a7a6b3dff2e830538e06d25934e9f14bf6b40ab5674fe648e314bf06f84282f5ef52bc1401de3a42eb66e64bcdadd2674348e5bdb7016feda44d719af387a948ad81cbaed10213dd930fc7bc7677d8c4cdab0645d0ff15e6ad6ca37135942c3be08f23e7be0992c8b3370dcdc31045e086d823107fb2e443dc9', 16)
c = int('a913a96e215b5aa79c702d27fa375c73d06787639c4131fb32877cafefaa8faf70e15f6a17ef2a9a6f5310b157cb287b740e77cb5385081d1853a9104bc16357b259fa2d146bd87398d4ef6f1c078289812952c67792cf9cd745049aeb9d4ab4dff2825a9c0b3381f19b2a67164f9d4de33c25f98bc2f224feb5507b531e1a1c7be5ed2d8ddd01f3fae37245e8cf99c75a21848993d445e1d6d69d555a3e6cc8055704fdde88df9084bda3ea65a9384fa64bf8df4d88946449526320c15d4d2d871638070489adf3f8c95caffeab40b0d137a9319be20cdf6ebbaf037f62093d9bd33edd4ffd7e1929b9ab06252956fd85250a0515ef2b4e035017be5702cdd3', 16)
e = 0x10001

# Pollard's p-1 attack
# p-1 and q-1 are smooth: all prime factors <= 2^16 (for p) and <= 2^17 (for q)
# All factors are distinct (enforced by the challenge code)
# So M = product of all primes <= 2^17 will be divisible by both p-1 and q-1

B = 2**17  # smoothness bound

print(f"[*] Running Pollard's p-1 with B = {B}")
print(f"[*] Computing primes up to B...")

a = 2
count = 0
for prime in primerange(2, B + 1):
    # For each prime, compute the highest power <= B
    pk = prime
    while pk * prime <= B:
        pk *= prime
    a = pow(a, pk, n)
    count += 1
    if count % 5000 == 0:
        print(f"    processed {count} primes...")
        g = gcd(a - 1, n)
        if 1 < g < n:
            print(f"[+] Found factor early! g = {g}")
            break

g = gcd(a - 1, n)
print(f"[*] gcd(a-1, n) = {g}")

if 1 < g < n:
    p = g
    q = n // p
    assert p * q == n, "Factorization check failed!"
    print(f"[+] Factored n!")
    print(f"    p = {p}")
    print(f"    q = {q}")

    m = lcm(p - 1, q - 1)
    d = pow(e, -1, m)
    flag_int = pow(c, d, n)
    flag_hex = hex(flag_int)[2:]
    if len(flag_hex) % 2:
        flag_hex = '0' + flag_hex
    flag = unhexlify(flag_hex).decode()
    print(f"\n[+] FLAG: {flag}")
else:
    print(f"[-] Failed: gcd = {g}")
    if g == 1:
        print("    B too small or different attack needed")
    elif g == n:
        print("    gcd = n, try different base or smaller B")
