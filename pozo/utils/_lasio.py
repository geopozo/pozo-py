import re

description_no_num = re.compile(r"^(?:\s*\d+\s+)?(.*)$")


def remove_lasio_suffix(mnemonic: str) -> str:
    return mnemonic.split(":", 1)[0] if ":" in mnemonic else mnemonic


def remove_prefix_number(descr: str) -> str:
    desc_match = description_no_num.findall(descr)
    return desc_match[0] if len(desc_match) > 0 else descr
