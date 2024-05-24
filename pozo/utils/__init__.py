import array as array

# These are all utility functions
# Taken by the principal __ini__.py
def deLASio(mnemonic):
    return mnemonic.split(":", 1)[0] if ":" in mnemonic else mnemonic
