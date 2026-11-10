import binascii

_B58_ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_B58_INDEX = {c: i for i, c in enumerate(_B58_ALPHABET)}


def _unhex(x: str) -> bytes:
    x = x.removeprefix("0x")
    return binascii.unhexlify(x)


def _b58_decode(s: str) -> bytes:
    n = 0
    for c in s.encode():
        try:
            n = n * 58 + _B58_INDEX[c]
        except KeyError:
            raise ValueError(f"invalid base58 character: {chr(c)!r}") from None
    full = n.to_bytes((n.bit_length() + 7) // 8, "big")
    pad = len(s) - len(s.lstrip("1"))
    return b"\x00" * pad + full


def _parse_key(s: str, encoding: str = "auto") -> bytes:
    if encoding == "hex":
        return _unhex(s)
    if encoding == "base58":
        return _b58_decode(s)
    if encoding != "auto":
        raise ValueError(f"unknown encoding {encoding!r}, expected one of: auto, hex, base58")
    if s.startswith("0x"):
        return _unhex(s)
    return _b58_decode(s)


def verify_ed25519(
    public_key: str,
    message: bytes,
    signature: str,
    *,
    encoding: str = "auto",
) -> bool:
    try:
        from nacl.signing import VerifyKey
        from nacl.exceptions import BadSignatureError
    except ImportError as e:
        raise RuntimeError("pynacl required") from e

    pk = _parse_key(public_key, encoding)
    sig = _parse_key(signature, encoding)
    try:
        VerifyKey(pk).verify(message, sig)
        return True
    except BadSignatureError:
        return False


def verify_evm_personal(address: str, message: bytes, signature: str) -> bool:
    try:
        from eth_account.messages import encode_defunct
        from eth_account import Account
    except ImportError as e:
        raise RuntimeError("eth-account required") from e

    recovered = Account.recover_message(encode_defunct(message), signature=signature)
    return recovered.lower() == address.lower()


def ton_safe_message(payload: bytes) -> bytes:
    return b"ton-safe-sign-magic" + payload


def solana_offchain_message(payload: bytes) -> bytes:
    return b"\xffsolana offchain" + payload


def evm_personal_hash(payload: bytes) -> bytes:
    try:
        from eth_utils import keccak
    except ImportError as e:
        raise RuntimeError("eth-utils required") from e
    prefix = f"\x19Ethereum Signed Message:\n{len(payload)}".encode()
    return keccak(prefix + payload)
