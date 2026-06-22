import pytest
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import config
import auth

class MockSessionState:
    """Mock session state supporting both dict and attribute access."""
    def __init__(self):
        self._data = {}
    
    def __setitem__(self, key, value):
        self._data[key] = value
        
    def __getitem__(self, key):
        return self._data[key]
        
    def __contains__(self, key):
        return key in self._data
        
    def get(self, key, default=None):
        return self._data.get(key, default)
        
    def clear(self):
        self._data.clear()
        
    def __setattr__(self, name, value):
        if name == "_data":
            object.__setattr__(self, name, value)
        else:
            self._data[name] = value
            
    def __getattribute__(self, name):
        if name == "_data" or name.startswith("__") or name in ("clear", "get"):
            return object.__getattribute__(self, name)
        try:
            _data = object.__getattribute__(self, "_data")
            if name in _data:
                return _data[name]
        except AttributeError:
            pass
        return object.__getattribute__(self, name)

def test_password_hashing():
    password = "MySecurePassword123"
    pwd_hash, salt = auth.hash_password(password)
    
    assert pwd_hash is not None
    assert salt is not None
    assert len(pwd_hash) > 0
    assert len(salt) > 0
    
    # Verification should succeed with correct password (returns (valid, needs_rehash) tuple)
    valid, _ = auth.verify_password(password, pwd_hash, salt)
    assert valid is True

    # Verification should fail with incorrect password
    assert auth.verify_password("wrong_password", pwd_hash, salt)[0] is False
    assert auth.verify_password("", pwd_hash, salt)[0] is False

def test_username_validation():
    # Valid usernames
    assert auth.is_valid_username("coach_john") is True
    assert auth.is_valid_username("john.doe@example.com") is True
    assert auth.is_valid_username("player-1") is True
    assert auth.is_valid_username("user123") is True
    
    # Invalid usernames
    assert auth.is_valid_username("jo") is False  # too short
    assert auth.is_valid_username("john doe") is False  # space not allowed
    assert auth.is_valid_username("usr#") is False  # illegal character

def test_user_signup_and_login_flow(tmp_path):
    # Prepare sandbox directories inside tmp_path
    data_dir = tmp_path / "data"
    prod_dir = data_dir / "production"
    prod_dir.mkdir(parents=True, exist_ok=True)
    
    # Create dummy seed files
    drill_lib = prod_dir / "drill_library.csv"
    with open(drill_lib, "w") as f:
        f.write("drill_id,drill_name\n1,Warmup Pass")
        
    mentor_feed = prod_dir / "mentor_feed.json"
    with open(mentor_feed, "w") as f:
        f.write('{"posts": []}')
        
    presenters = data_dir / "presenters.csv"
    with open(presenters, "w") as f:
        f.write("presenter_id,full_name\n1,Presenter A")
        
    mock_session = MockSessionState()
    
    # In-memory mock database
    mock_db_users = {}
    
    def mock_get_user(username):
        return mock_db_users.get(username)
        
    def mock_create_user(username, password_hash, salt):
        if username in mock_db_users:
            raise RuntimeError("Username already exists")
        mock_db_users[username] = {
            "username": username,
            "password_hash": password_hash,
            "salt": salt
        }

    # Patch config paths and db methods
    with patch("config.PRODUCTION_DATA_DIR", prod_dir), \
         patch("config.DATA_DIR", data_dir), \
         patch("streamlit.error") as mock_error, \
         patch("streamlit.success") as mock_success, \
         patch("streamlit.session_state", mock_session), \
         patch("db.get_user", side_effect=mock_get_user), \
         patch("db.create_user", side_effect=mock_create_user):
         
        # Ensure users database is empty initially
        assert mock_db_users == {}
        
        # Test signup
        signup_ok = auth.signup_user("test_user", "password123")
        assert signup_ok is True
        
        # Check users database contains the entry
        assert "test_user" in mock_db_users
        assert "password_hash" in mock_db_users["test_user"]
        assert "salt" in mock_db_users["test_user"]
        
        # Check isolated directory was bootstrapped
        user_dir = prod_dir / "users" / "test_user"
        assert user_dir.exists()
        assert (user_dir / "drill_library.csv").exists()
        assert (user_dir / "mentor_feed.json").exists()
        assert (user_dir / "presenters.csv").exists()
        
        # Test login
        login_ok = auth.login_user("test_user", "password123")
        assert login_ok is True
        assert mock_session.authenticated is True
        assert mock_session.username == "test_user"
        assert mock_session.data_path == user_dir
        
        # Test login with invalid password
        login_fail = auth.login_user("test_user", "wrong_pwd")
        assert login_fail is False
        
        # Test signup duplicate username
        dup_signup = auth.signup_user("test_user", "newpassword")
        assert dup_signup is False
        mock_error.assert_any_call("Username is already taken.")


