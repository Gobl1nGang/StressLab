import unittest
from validator import SQLDataValidator, StrategyData, QueryFilter, validate_sql_data, safe_sql_fetch

"""
run with:
    cd /Users/rafeeahsan/StressLab/security
    python test_validator.py
"""

class TestSQLDataValidator(unittest.TestCase):
    
    def test_safe_column_names(self):
        """Test valid column names pass validation"""
        self.assertTrue(SQLDataValidator.validate_column_name('username'))
        self.assertTrue(SQLDataValidator.validate_column_name('email'))
        self.assertTrue(SQLDataValidator.validate_column_name('id'))
    
    def test_safe_operators(self):
        """Test valid operators pass validation"""
        self.assertTrue(SQLDataValidator.validate_operator('='))
        self.assertTrue(SQLDataValidator.validate_operator('LIKE'))
        self.assertTrue(SQLDataValidator.validate_operator('>='))
    
    def test_safe_strings_no_injection(self):
        """Test clean strings are not flagged as injection"""
        safe_strings = ['johndoe', 'test@email.com', 'My Strategy', 'AAPL', '123.45']
        for string in safe_strings:
            self.assertFalse(SQLDataValidator.detect_sql_injection(string))
    
    def test_sanitize_safe_inputs(self):
        """Test sanitization of safe inputs"""
        self.assertEqual(SQLDataValidator.sanitize_input('johndoe'), 'johndoe')
        self.assertEqual(SQLDataValidator.sanitize_input('test@email.com'), 'test@email.com')
        self.assertEqual(SQLDataValidator.sanitize_input('AAPL'), 'AAPL')

class TestStrategyData(unittest.TestCase):
    
    def test_valid_strategy_data(self):
        """Test valid strategy data passes validation"""
        data = {
            'strategy_name': 'My Trading Strategy',
            'symbol': 'AAPL',
            'username': 'johndoe'
        }
        result = validate_sql_data(data, StrategyData)
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['username'], 'johndoe')

class TestQueryFilter(unittest.TestCase):
    
    def test_valid_query_filter(self):
        """Test valid query filter passes validation"""
        data = {
            'column': 'username',
            'operator': '=',
            'value': 'johndoe'
        }
        result = validate_sql_data(data, QueryFilter)
        self.assertEqual(result['column'], 'username')
        self.assertEqual(result['operator'], '=')

class TestSafeSQLFetch(unittest.TestCase):
    
    def test_safe_sql_results(self):
        """Test processing of safe SQL results"""
        query_result = [('johndoe', 'test@email.com', 1)]
        columns = ['username', 'email', 'id']
        result = safe_sql_fetch(query_result, columns)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['username'], 'johndoe')

class TestDangerousInputs(unittest.TestCase):
    
    def test_sql_injection_detection(self):
        """Test detection of SQL injection patterns"""
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "admin'--",
            "UNION SELECT * FROM passwords",
            "'; exec xp_cmdshell('dir'); --",
            "/* comment */ SELECT",
            "# comment",
            "&#39; DROP TABLE users",
            "&quot; UNION SELECT",
            "%27 OR 1=1",
            "%22 DELETE FROM",
            "\\x27 INSERT INTO",
            "\\u0027 UPDATE SET"
        ]
        for dangerous in dangerous_inputs:
            self.assertTrue(SQLDataValidator.detect_sql_injection(dangerous))
    
    def test_invalid_columns_rejected(self):
        """Test invalid column names are rejected"""
        invalid_columns = ['password', 'secret', 'admin_table', 'DROP', 'SELECT']
        for column in invalid_columns:
            self.assertFalse(SQLDataValidator.validate_column_name(column))
    
    def test_invalid_operators_rejected(self):
        """Test invalid operators are rejected"""
        invalid_operators = ['DROP', 'DELETE', 'EXEC', 'UNION', 'INSERT']
        for operator in invalid_operators:
            self.assertFalse(SQLDataValidator.validate_operator(operator))
    
    def test_dangerous_strategy_data_rejected(self):
        """Test dangerous strategy data raises validation errors"""
        dangerous_data = [
            {'strategy_name': "'; DROP TABLE strategies; --", 'symbol': 'AAPL', 'username': 'johndoe'},
            {'strategy_name': 'Valid Strategy', 'symbol': 'AAPL', 'username': "admin'--"},
            {'strategy_name': 'Valid Strategy', 'symbol': 'TOOLONGERTHAN10', 'username': 'johndoe'},
            {'strategy_name': 'UNION SELECT', 'symbol': 'AAPL', 'username': 'johndoe'}
        ]
        for data in dangerous_data:
            with self.assertRaises(ValueError):
                validate_sql_data(data, StrategyData)
    
    def test_dangerous_query_filter_rejected(self):
        """Test dangerous query filters are rejected"""
        dangerous_filters = [
            {'column': 'password', 'operator': '=', 'value': 'test'},
            {'column': 'username', 'operator': 'DROP', 'value': 'test'},
            {'column': 'username', 'operator': '=', 'value': "'; DROP TABLE users; --"}
        ]
        for filter_data in dangerous_filters:
            with self.assertRaises(ValueError):
                validate_sql_data(filter_data, QueryFilter)
    
    def test_sanitize_dangerous_inputs_raises_error(self):
        """Test sanitization raises errors for dangerous inputs"""
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "UNION SELECT password FROM users",
            "DELETE FROM table",
            "INSERT INTO users"
        ]
        for dangerous in dangerous_inputs:
            with self.assertRaises(ValueError):
                SQLDataValidator.sanitize_input(dangerous)

if __name__ == '__main__':
    unittest.main()