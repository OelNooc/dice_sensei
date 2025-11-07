#!/usr/bin/env python3
"""
Tests para el módulo de actualizaciones de DiceSensei
"""

import unittest
import tempfile
import json
import shutil
from pathlib import Path
import sys
import os

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from updater import DiceSenseiUpdater

class TestDiceSenseiUpdater(unittest.TestCase):
    
    def setUp(self):
        """Configuración antes de cada test"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir()
        
        self.version_file = self.config_dir / "version.json"
        with open(self.version_file, 'w') as f:
            json.dump({"version": "1.0.0"}, f)
    
    def tearDown(self):
        """Limpieza después de cada test"""
        shutil.rmtree(self.temp_dir)
    
    def test_version_parsing(self):
        """Test para el parsing de versiones"""
        updater = DiceSenseiUpdater(config_dir=str(self.config_dir))
        
        test_cases = [
            ("1.0.0", "1.0.1", True),   # Nueva versión mayor
            ("1.0.0", "1.1.0", True),   # Nueva versión menor  
            ("1.0.0", "2.0.0", True),   # Nueva versión mayor
            ("1.0.0", "1.0.0", False),  # Misma versión
            ("1.1.0", "1.0.0", False),  # Versión anterior
            ("2.0.0", "1.9.0", False),  # Versión anterior
        ]
        
        for current, latest, expected in test_cases:
            with self.subTest(current=current, latest=latest):
                result = updater.is_newer_version(latest, current)
                self.assertEqual(result, expected)
    
    def test_version_file_creation(self):
        """Test para la creación del archivo de versión"""
        updater = DiceSenseiUpdater(config_dir=str(self.config_dir))
        
        version = updater.get_current_version()
        self.assertEqual(version, "1.0.0")
        
        self.version_file.unlink()
        version = updater.get_current_version()
        self.assertEqual(version, "1.0.0")  # Valor por defecto
    
    def test_hash_calculation(self):
        """Test para el cálculo de hashes"""
        updater = DiceSenseiUpdater(config_dir=str(self.config_dir))
        
        test_file = Path(self.temp_dir) / "test.txt"
        test_content = "Hola DiceSensei - Este es un archivo de prueba"
        test_file.write_text(test_content, encoding='utf-8')
        
        calculated_hash = updater.calculate_hash(test_file)
        
        self.assertIsNotNone(calculated_hash)
        self.assertEqual(len(calculated_hash), 64)  
        
        same_hash = updater.calculate_hash(test_file)
        self.assertEqual(calculated_hash, same_hash)
    
    def test_file_size_verification(self):
        """Test para verificación de tamaño de archivo"""
        updater = DiceSenseiUpdater(config_dir=str(self.config_dir))
        
        test_file = Path(self.temp_dir) / "test.bin"
        test_content = b"x" * 1024  
        test_file.write_bytes(test_content)
        
        asset_info = {"size": 1024}
        
        result = updater.verify_file_size(test_file, asset_info)
        self.assertTrue(result)
        
        asset_info["size"] = 512
        result = updater.verify_file_size(test_file, asset_info)
        self.assertFalse(result)

class TestVersionComparison(unittest.TestCase):
    """Tests específicos para comparación de versiones"""

    def setUp(self):
        """Configuración antes de cada test"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir()
    
    def tearDown(self):
        """Limpieza después de cada test"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_version_format(self):
        """Test para diferentes formatos de versión"""
        updater = DiceSenseiUpdater(config_dir=str(self.config_dir))
        
        result = updater.is_newer_version("v1.1.0", "v1.0.0")
        self.assertTrue(result)
        
        result = updater.is_newer_version("1.1.0", "1.0.0")
        self.assertTrue(result)
        
        result = updater.is_newer_version("v2.0.0", "1.9.0")
        self.assertTrue(result)
    
    def test_invalid_versions(self):
        """Test para versiones inválidas"""
        updater = DiceSenseiUpdater(config_dir=str(self.config_dir))
        
        invalid_cases = [
            ("invalid", "1.0.0"),
            ("1.0", "1.0.0"),
            ("1.0.0", "invalid"),
            ("", "1.0.0"),
            ("1.0.0", "")
        ]
        
        for latest, current in invalid_cases:
            with self.subTest(latest=latest, current=current):
                result = updater.is_newer_version(latest, current)
                self.assertFalse(result)

class TestUpdaterInitialization(unittest.TestCase):
    """Tests específicos para inicialización del updater"""
    
    def test_updater_without_config_dir(self):
        """Test que el updater funciona sin directorio de config existente"""
        temp_dir = tempfile.mkdtemp()
        try:
            # Directorio que no existe
            non_existent_dir = Path(temp_dir) / "non_existent_config"
            
            # Debería crearse automáticamente
            updater = DiceSenseiUpdater(config_dir=str(non_existent_dir))
            
            # Debería tener versión por defecto
            self.assertEqual(updater.current_version, "1.0.0")
            self.assertTrue(non_existent_dir.exists())
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_updater_with_invalid_version_file(self):
        """Test con archivo de versión corrupto"""
        temp_dir = tempfile.mkdtemp()
        try:
            config_dir = Path(temp_dir) / "config"
            config_dir.mkdir()
            
            version_file = config_dir / "version.json"
            version_file.write_text("invalid json content")
            
            updater = DiceSenseiUpdater(config_dir=str(config_dir))
            self.assertEqual(updater.current_version, "1.0.0")
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    unittest.main(verbosity=2)