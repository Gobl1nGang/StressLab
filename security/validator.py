import re
import html
import unicodedata
import requests
from typing import List, Optional, Any
from pydantic import BaseModel, validator, ValidationError

class SQLDataValidator:
    # Allow lists
    ALLOWED_COLUMNS = {'id', 'username', 'email', 'strategy_name', 'symbol', 'timestamp', 'price', 'volume'}
    ALLOWED_OPERATORS = {'=', '>', '<', '>=', '<=', 'LIKE', 'IN'}
    ALLOWED_FUNCTIONS = {'COUNT', 'SUM', 'AVG', 'MAX', 'MIN'}
    
    # Injection patterns
    SQL_INJECTION_PATTERNS = [
        # uses regex expressions to check for potentially dangerous sequences
        r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(or|and)\s+\d+\s*=\s*\d+)",
        r"(\bor\s+1\s*=\s*1\b)",
        r"(\';|\"\;)",
        r"(\bxp_cmdshell\b)",
        r"(\bsp_executesql\b)",
        r"(&#39;|&quot;|%27|%22)",
        r"(\\x27|\\x22|\\u0027|\\u0022)",
        r"([\u0000-\u001f\u007f-\u009f])",
        r"([\u2000-\u206f\u2e00-\u2e7f])",
        r"(;\s*$|;\s*--)",
        r"(\r\n|\n|\r).*?(union|select|drop|delete)",
        r"(\\n|\\r|\\t)",
        r"(\x0a|\x0d|\x09)"

    ]

    # Normalize and validate Unicode input to reduce character differences
    @classmethod
    def normalize_unicode(cls, value: str) -> str:
        """Normalize Unicode to prevent dangerous characters"""
        if not isinstance(value, str):
            value = str(value)
        
        # Normalize to NFC form
        normalized = unicodedata.normalize('NFC', value)
        
        # Remove control characters
        cleaned = ''.join(char for char in normalized if unicodedata.category(char) not in ['Cc', 'Cf'])
        
        return cleaned

    # Check if column name is in allowed list
    @classmethod
    def validate_column_name(cls, column: str) -> bool:
        """Validate column name against allow list"""
        return column.lower() in cls.ALLOWED_COLUMNS
    
    # Check if SQL operator is in allowed list
    @classmethod
    def validate_operator(cls, operator: str) -> bool:
        """Validate SQL operator against allow list"""
        return operator.upper() in cls.ALLOWED_OPERATORS
    
    # Escape single quotes and HTML entities to prevent injection
    @classmethod
    def escape_sql_string(cls, value: str) -> str:
        """Escape SQL string to prevent injection"""
        if not isinstance(value, str):
            return str(value)
        
        # Replace single quotes with double single quotes
        escaped = value.replace("'", "''")
        # HTML escape for additional safety
        escaped = html.escape(escaped)
        return escaped
    
    # Scan input for SQL injection patterns using regex
    @classmethod
    def detect_sql_injection(cls, input_str: str) -> bool:
        """Detect potential SQL injection patterns"""
        if not isinstance(input_str, str):
            return False
            
        input_lower = input_str.lower()
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                return True
        return False
    
    # Convert input to string, check for injection, and escape
    @classmethod
    def sanitize_input(cls, value: Any) -> str:
        """Sanitize input value"""
        if value is None:
            return ""
        
        str_value = str(value).strip()
        
        # Normalize Unicode
        str_value = cls.normalize_unicode(str_value)
        
        # Check for injection
        if cls.detect_sql_injection(str_value):
            raise ValueError("Potential SQL injection detected")
        
        # Escape and return
        return cls.escape_sql_string(str_value)

    # Normalize dictionary values with Unicode validation
    @classmethod
    def normalize_dict_values(cls, data: dict) -> dict:
        """Normalize Unicode for all string values in dictionary"""
        normalized_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                normalized_data[key] = cls.normalize_unicode(value)
            else:
                normalized_data[key] = value
        return normalized_data

class UserCredentials(BaseModel):
    """Bean validation model for user credentials"""
    username: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', v):
            raise ValueError('Invalid username format')
        if SQLDataValidator.detect_sql_injection(v):
            raise ValueError('Invalid characters in username')
        return SQLDataValidator.sanitize_input(v)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8 or len(v) > 128:
            raise ValueError('Password must be 8-128 characters')
        if SQLDataValidator.detect_sql_injection(v):
            raise ValueError('Invalid characters in password')
        return SQLDataValidator.sanitize_input(v)

class StrategyData(BaseModel):
    """Bean validation model for strategy data"""
    strategy_name: str
    symbol: str
    username: str
    
    @validator('strategy_name')
    def validate_strategy_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9_\-\s]{1,50}$', v):
            raise ValueError('Invalid strategy name format')
        if SQLDataValidator.detect_sql_injection(v):
            raise ValueError('Invalid characters in strategy name')
        return SQLDataValidator.sanitize_input(v)
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not re.match(r'^[A-Z]{1,10}$', v):
            raise ValueError('Invalid symbol format')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', v):
            raise ValueError('Invalid username format')
        if SQLDataValidator.detect_sql_injection(v):
            raise ValueError('Invalid characters in username')
        return SQLDataValidator.sanitize_input(v)

class QueryFilter(BaseModel):
    """Bean validation for query filters"""
    column: str
    operator: str
    value: str
    
    @validator('column')
    def validate_column(cls, v):
        if not SQLDataValidator.validate_column_name(v):
            raise ValueError(f'Column not allowed: {v}')
        return v
    
    @validator('operator')
    def validate_operator(cls, v):
        if not SQLDataValidator.validate_operator(v):
            raise ValueError(f'Operator not allowed: {v}')
        return v
    
    @validator('value')
    def validate_value(cls, v):
        return SQLDataValidator.sanitize_input(v)

# Validate credentials dictionary and return it or error message
def process_credentials(credentials: dict):
    """Validate credentials dictionary - return dict if safe, error message if not"""
    try:
        # Validate credentials
        validated_creds = validate_credentials(credentials)
        return validated_creds
        
    except ValueError as e:
        return str(e)

# Validate username/password dictionary and return original if safe
def validate_credentials(credentials: dict) -> dict:
    """Validate username/password dictionary - return original if safe"""
    try:
        # Use the Pydantic model to validate the dictionary
        UserCredentials(**credentials)
        return credentials
    except ValidationError as e:
        # Extract the error message from Pydantic's ValidationError
        raise ValueError(e.errors()[0]['msg'])

# Validate dictionary data using Pydantic models
def validate_sql_data(data: dict, model_class: BaseModel) -> dict:
    """Validate SQL data using bean validation"""
    try:
        validated = model_class(**data)
        return validated.dict()
    except ValidationError as e:
        raise ValueError(f"Validation failed: {e}")

# Process SQL query results and validate each field
def safe_sql_fetch(query_result: List[tuple], expected_columns: List[str]) -> List[dict]:
    """Safely process SQL query results"""
    validated_results = []
    
    for row in query_result:
        if len(row) != len(expected_columns):
            continue
            
        row_dict = {}
        for i, column in enumerate(expected_columns):
            if SQLDataValidator.validate_column_name(column):
                raw_value = row[i] if i < len(row) else None
                row_dict[column] = SQLDataValidator.sanitize_input(raw_value)
        
        validated_results.append(row_dict)
    
    return validated_results