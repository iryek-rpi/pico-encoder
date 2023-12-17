import w5500 as w
nic = w.get_nic()
m = nic.config('mac')
h = m.hex()
print(f'mac: {m} {h}')

#>>> m
#b"\x02\x93'|b\x9a"
#>>> h
#'0293277c629a'
#>>> 