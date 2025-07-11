def remove_lasio_suffix(mnemonic: str) -> str:
    return mnemonic.split(":", 1)[0] if ":" in mnemonic else mnemonic
