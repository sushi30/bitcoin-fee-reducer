from bit import PrivateKeyTestnet

a = PrivateKeyTestnet()
print(a.to_wif())
print(a.address)
b = PrivateKeyTestnet()
print(b.to_wif())
print(b.address)
