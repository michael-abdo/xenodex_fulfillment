import pytest
import logging
import tempfile
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.utils import setup_logging, validate_file, get_file_duration


class TestSetupLogging:
    def test_setup_logging_basic(self, caplog):
        """Test basic logging setup"""
        config = {
            'logging': {
                'level': 'INFO',
                'format': '%(levelname)s - %(message)s'
            }
        }
        
        logger = setup_logging(config)
        assert isinstance(logger, logging.Logger)
        
        # Test logging
        logger.info("Test message")
        assert "Test message" in caplog.text
    
    def test_setup_logging_debug_level(self, caplog):
        """Test logging with DEBUG level"""
        config = {
            'logging': {
                'level': 'DEBUG',
                'format': '%(message)s'
            }
        }
        
        logger = setup_logging(config)
        logger.debug("Debug message")
        logger.info("Info message")
        
        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text
    
    def test_setup_logging_default_config(self):
        """Test logging with default configuration"""
        logger = setup_logging({})
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO


class TestValidateFile:
    def test_validate_existing_file(self):
        """Test validating an existing file"""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b"fake audio data")
            f.flush()
            
            # Should return the path for existing file
            result = validate_file(f.name)
            assert result == Path(f.name)
            
            # Cleanup
            Path(f.name).unlink()
    
    def test_validate_nonexistent_file(self):
        """Test validating a non-existent file"""
        with pytest.raises(FileNotFoundError) as exc_info:
            validate_file("/nonexistent/file.mp3")
        assert "not found" in str(exc_info.value).lower()
    
    def test_validate_directory(self):
        """Test validating a directory instead of file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError) as exc_info:
                validate_file(tmpdir)
            assert "not a file" in str(exc_info.value).lower()
    
    def test_validate_unsupported_extension(self):
        """Test validating file with unsupported extension"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"text content")
            f.flush()
            
            with pytest.raises(ValueError) as exc_info:
                validate_file(f.name)
            assert "Unsupported file type" in str(exc_info.value)
            
            # Cleanup
            Path(f.name).unlink()
    
    def test_validate_supported_extensions(self):
        """Test validating files with supported extensions"""
        supported_extensions = ['.mp3', '.wav', '.mp4', '.m4a', '.flac', '.ogg']
        
        for ext in supported_extensions:
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                f.write(b"fake media data")
                f.flush()
                
                result = validate_file(f.name)
                assert result == Path(f.name)
                
                # Cleanup
                Path(f.name).unlink()


class TestGetFileDuration:
    def test_get_duration_unsupported_file(self):
        """Test getting duration returns None for unsupported files"""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b"not real audio data")
            f.flush()
            
            # Should return None for invalid/unsupported files
            duration = get_file_duration(Path(f.name))
            assert duration is None
            
            # Cleanup
            Path(f.name).unlink()
    
    def test_get_duration_nonexistent_file(self):
        """Test getting duration for non-existent file"""
        duration = get_file_duration(Path("/nonexistent/file.mp3"))
        assert duration is None


class TestUtilityFunctions:
    def test_imports(self):
        """Test that all expected functions are importable"""
        from shared.utils import setup_logging, validate_file, get_file_duration
        assert callable(setup_logging)
        assert callable(validate_file)
        assert callable(get_file_duration)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])