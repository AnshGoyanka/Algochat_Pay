"""
Utility functions for AlgoChat Pay
Common helpers used across the application
"""
import re
from datetime import datetime
from typing import Optional


def format_algo_amount(microalgos: int) -> float:
    """Convert microALGOs to ALGO"""
    return microalgos / 1_000_000


def format_microalgos(algo: float) -> int:
    """Convert ALGO to microALGOs"""
    return int(algo * 1_000_000)


def shorten_address(address: str, prefix: int = 8, suffix: int = 6) -> str:
    """
    Shorten Algorand address for display
    Example: ABCD...XYZ123
    """
    if len(address) <= prefix + suffix:
        return address
    return f"{address[:prefix]}...{address[-suffix:]}"


def shorten_tx_id(tx_id: str, length: int = 16) -> str:
    """Shorten transaction ID for display"""
    return tx_id[:length] + "..." if len(tx_id) > length else tx_id


def format_timestamp(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime for human-readable display"""
    return dt.strftime(format)


def parse_phone_number(phone: str) -> Optional[str]:
    """
    Parse and normalize phone number
    Accepts: +919876543210, 9876543210, +91 9876543210
    Returns: +919876543210 or None
    """
    # Remove all non-digit characters except +
    cleaned = re.sub(r"[^\d+]", "", phone)
    
    # Add + if missing
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    
    # Validate length (10-15 digits after +)
    digits = cleaned[1:]
    if 10 <= len(digits) <= 15 and digits.isdigit():
        return cleaned
    
    return None


def calculate_fee(amount: float, fee_algo: float = 0.001) -> float:
    """Calculate total cost including network fee"""
    return amount + fee_algo


def format_currency(amount: float, currency: str = "ALGO", decimals: int = 4) -> str:
    """Format amount with currency symbol"""
    return f"{amount:.{decimals}f} {currency}"


def validate_amount(amount: float) -> bool:
    """Validate payment amount"""
    return amount > 0 and amount < 1_000_000  # Max 1M ALGO


def generate_note(note_type: str, metadata: dict = None) -> str:
    """
    Generate transaction note
    
    Args:
        note_type: Type of transaction (payment, split, fund, ticket)
        metadata: Additional metadata dict
    
    Returns:
        Formatted note string
    """
    base_note = f"AlgoChat Pay - {note_type}"
    
    if metadata:
        meta_str = " | ".join([f"{k}:{v}" for k, v in metadata.items()])
        return f"{base_note} | {meta_str}"
    
    return base_note


def extract_numbers(text: str) -> list[float]:
    """Extract all numbers from text"""
    pattern = r'\d+\.?\d*'
    matches = re.findall(pattern, text)
    return [float(m) for m in matches]


def chunked_list(items: list, chunk_size: int) -> list:
    """Split list into chunks"""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division with default for zero denominator"""
    return numerator / denominator if denominator != 0 else default


def percentage(part: float, total: float) -> float:
    """Calculate percentage"""
    return safe_divide(part, total) * 100


def is_testnet_address(address: str) -> bool:
    """Check if address is valid Algorand address format"""
    return len(address) == 58 and address.isalnum()


# Time helpers
def seconds_to_human(seconds: int) -> str:
    """Convert seconds to human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
