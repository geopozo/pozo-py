import array as array

# deLASio function has 1 parameter, this return a mnemonic
def deLASio(mnemonic):
    return mnemonic.split(":", 1)[0] if ":" in mnemonic else mnemonic
