"""Utilities for Indian market (NSE/BSE) ticker normalization and calendar."""

from datetime import datetime, timedelta
from typing import Optional


# Indian market holidays for 2024-2025
INDIAN_MARKET_HOLIDAYS = [
    # 2024
    "2024-01-26",  # Republic Day
    "2024-03-08",  # Maha Shivaratri
    "2024-03-25",  # Holi
    "2024-03-29",  # Good Friday
    "2024-04-11",  # Id-Ul-Fitr
    "2024-04-17",  # Ram Navami
    "2024-04-21",  # Mahavir Jayanti
    "2024-05-01",  # Maharashtra Day
    "2024-05-23",  # Buddha Purnima
    "2024-06-17",  # Bakri Id
    "2024-07-17",  # Muharram
    "2024-08-15",  # Independence Day
    "2024-08-26",  # Janmashtami
    "2024-10-02",  # Gandhi Jayanti
    "2024-10-12",  # Dussehra
    "2024-10-31",  # Diwali Laxmi Pujan
    "2024-11-01",  # Diwali Balipratipada
    "2024-11-15",  # Gurunanak Jayanti
    "2024-12-25",  # Christmas
    
    # 2025
    "2025-01-26",  # Republic Day
    "2025-02-26",  # Maha Shivaratri
    "2025-03-14",  # Holi
    "2025-03-31",  # Id-Ul-Fitr
    "2025-04-10",  # Mahavir Jayanti
    "2025-04-14",  # Dr. Ambedkar Jayanti
    "2025-04-18",  # Good Friday
    "2025-05-01",  # Maharashtra Day
    "2025-05-12",  # Buddha Purnima
    "2025-06-07",  # Bakri Id
    "2025-07-05",  # Muharram
    "2025-08-15",  # Independence Day
    "2025-08-16",  # Parsi New Year
    "2025-08-27",  # Janmashtami
    "2025-10-02",  # Gandhi Jayanti
    "2025-10-02",  # Dussehra
    "2025-10-20",  # Diwali Laxmi Pujan
    "2025-10-21",  # Diwali Balipratipada
    "2025-11-05",  # Gurunanak Jayanti
    "2025-12-25",  # Christmas
]


# Indian stock sector mapping (major stocks)
INDIAN_SECTOR_MAPPING = {
    # Energy
    "RELIANCE": "Energy",
    "ONGC": "Energy",
    "BPCL": "Energy",
    "IOC": "Energy",
    "GAIL": "Energy",
    
    # IT
    "TCS": "IT",
    "INFY": "IT",
    "WIPRO": "IT",
    "HCLTECH": "IT",
    "TECHM": "IT",
    "LTI": "IT",
    "MPHASIS": "IT",
    "COFORGE": "IT",
    
    # Banking
    "HDFCBANK": "Banking",
    "ICICIBANK": "Banking",
    "SBIN": "Banking",
    "KOTAKBANK": "Banking",
    "AXISBANK": "Banking",
    "INDUSINDBK": "Banking",
    "BANDHANBNK": "Banking",
    "FEDERALBNK": "Banking",
    "PNB": "Banking",
    "BANKBARODA": "Banking",
    
    # Financial Services
    "BAJFINANCE": "Financial Services",
    "BAJAJFINSV": "Financial Services",
    "HDFCLIFE": "Financial Services",
    "SBILIFE": "Financial Services",
    "ICICIGI": "Financial Services",
    "ICICIPRULI": "Financial Services",
    
    # Telecom
    "BHARTIARTL": "Telecom",
    "IDEA": "Telecom",
    
    # Pharma
    "SUNPHARMA": "Pharma",
    "DRREDDY": "Pharma",
    "CIPLA": "Pharma",
    "DIVISLAB": "Pharma",
    "BIOCON": "Pharma",
    "AUROPHARMA": "Pharma",
    "LUPIN": "Pharma",
    
    # Auto
    "MARUTI": "Auto",
    "M&M": "Auto",
    "TATAMOTORS": "Auto",
    "BAJAJ-AUTO": "Auto",
    "HEROMOTOCO": "Auto",
    "EICHERMOT": "Auto",
    "TVSMOTOR": "Auto",
    
    # FMCG
    "HINDUNILVR": "FMCG",
    "ITC": "FMCG",
    "NESTLEIND": "FMCG",
    "BRITANNIA": "FMCG",
    "DABUR": "FMCG",
    "MARICO": "FMCG",
    "GODREJCP": "FMCG",
    
    # Metals
    "TATASTEEL": "Metals",
    "HINDALCO": "Metals",
    "JSWSTEEL": "Metals",
    "VEDL": "Metals",
    "COALINDIA": "Metals",
    "NMDC": "Metals",
    
    # Cement
    "ULTRACEMCO": "Cement",
    "GRASIM": "Cement",
    "SHREECEM": "Cement",
    "AMBUJACEM": "Cement",
    "ACC": "Cement",
    
    # Infrastructure
    "LT": "Infrastructure",
    "ADANIPORTS": "Infrastructure",
    "POWERGRID": "Infrastructure",
    "NTPC": "Infrastructure",
}


def normalize_indian_ticker(symbol: str) -> str:
    """Convert Indian ticker to yfinance format.
    
    Appends .NS suffix for NSE by default if no suffix present.
    Preserves existing .NS or .BO suffixes.
    
    Args:
        symbol: Stock ticker symbol (e.g., "RELIANCE", "TCS", "INFY.NS")
    
    Returns:
        Normalized ticker with exchange suffix (e.g., "RELIANCE.NS")
    
    Examples:
        >>> normalize_indian_ticker("RELIANCE")
        'RELIANCE.NS'
        >>> normalize_indian_ticker("TCS.NS")
        'TCS.NS'
        >>> normalize_indian_ticker("INFY.BO")
        'INFY.BO'
    """
    if not symbol:
        return symbol
    
    # Already has suffix, return as-is
    if symbol.endswith('.NS') or symbol.endswith('.BO'):
        return symbol
    
    # Default to NSE
    return f"{symbol}.NS"


def is_indian_ticker(symbol: str) -> bool:
    """Check if ticker is an Indian market ticker.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        True if ticker ends with .NS or .BO, False otherwise
    
    Examples:
        >>> is_indian_ticker("RELIANCE.NS")
        True
        >>> is_indian_ticker("TCS.BO")
        True
        >>> is_indian_ticker("AAPL")
        False
    """
    if not symbol:
        return False
    return symbol.endswith('.NS') or symbol.endswith('.BO')


def is_indian_market_open(date: datetime) -> bool:
    """Check if Indian market is open on given date.
    
    Market is closed on weekends (Saturday, Sunday) and holidays.
    
    Args:
        date: Date to check
    
    Returns:
        True if market is open, False otherwise
    
    Examples:
        >>> is_indian_market_open(datetime(2024, 1, 26))  # Republic Day
        False
        >>> is_indian_market_open(datetime(2024, 1, 27))  # Saturday
        False
        >>> is_indian_market_open(datetime(2024, 1, 29))  # Monday
        True
    """
    # Check if weekend
    if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Check if holiday
    date_str = date.strftime("%Y-%m-%d")
    if date_str in INDIAN_MARKET_HOLIDAYS:
        return False
    
    return True


def get_next_trading_day(date: datetime) -> datetime:
    """Get next Indian trading day after given date.
    
    Skips weekends and holidays.
    
    Args:
        date: Starting date
    
    Returns:
        Next trading day
    
    Examples:
        >>> get_next_trading_day(datetime(2024, 1, 26))  # Republic Day (Friday)
        datetime(2024, 1, 29)  # Next Monday
    """
    next_day = date + timedelta(days=1)
    
    # Keep incrementing until we find a trading day
    while not is_indian_market_open(next_day):
        next_day += timedelta(days=1)
    
    return next_day


def get_indian_sector(symbol: str) -> str:
    """Get sector for Indian stock.
    
    Args:
        symbol: Stock ticker symbol (with or without .NS/.BO suffix)
    
    Returns:
        Sector name or "Unknown" if not in mapping
    
    Examples:
        >>> get_indian_sector("RELIANCE.NS")
        'Energy'
        >>> get_indian_sector("TCS")
        'IT'
        >>> get_indian_sector("UNKNOWN")
        'Unknown'
    """
    # Remove exchange suffix
    base_symbol = symbol.replace('.NS', '').replace('.BO', '')
    return INDIAN_SECTOR_MAPPING.get(base_symbol, "Unknown")


def get_sector_peers(symbol: str, n: int = 5) -> list[str]:
    """Get peer stocks in same sector.
    
    Args:
        symbol: Stock ticker symbol
        n: Maximum number of peers to return (default 5)
    
    Returns:
        List of peer ticker symbols (without exchange suffix)
    
    Examples:
        >>> get_sector_peers("TCS.NS", n=3)
        ['INFY', 'WIPRO', 'HCLTECH']
        >>> get_sector_peers("RELIANCE", n=2)
        ['ONGC', 'BPCL']
    """
    sector = get_indian_sector(symbol)
    
    if sector == "Unknown":
        return []
    
    # Remove exchange suffix from input symbol
    base_symbol = symbol.replace('.NS', '').replace('.BO', '')
    
    # Find all stocks in same sector, excluding the input symbol
    peers = [
        ticker for ticker, sec in INDIAN_SECTOR_MAPPING.items()
        if sec == sector and ticker != base_symbol
    ]
    
    return peers[:n]
