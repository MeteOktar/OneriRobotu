import unittest
import os
import sys
import time
import pickle
import pandas as pd
from pathlib import Path
from Suggestor import Suggestor  # Öneri sisteminin ana kodu

# 🔹 1️⃣ Pickle Dosyalarının Yüklenme Testi
class TestLoadingPickleFiles(unittest.TestCase):
    """Pickle dosyalarının düzgün yüklendiğini test eder"""

    def setUp(self):
        """Test öncesi pickle dosyalarının var olup olmadığını kontrol eder."""
        self.smd_path = Path("OneriRobotu/archive/smd.pkl")
        self.ratings_path = Path("OneriRobotu/archive/ratings.pkl")

    def test_loading_existing_pickles(self):
        """Pickle dosyaları varsa, CSV işlemleri atlanmalı ve hızlı yüklenmeli."""
        self.assertTrue(self.smd_path.is_file(), "smd.pkl bulunamadı!")
        self.assertTrue(self.ratings_path.is_file(), "ratings.pkl bulunamadı!")

        start_time = time.time()
        suggestor = Suggestor()
        elapsed_time = time.time() - start_time

        self.assertTrue(hasattr(suggestor, "smd"), "smd.pkl yüklenmedi!")
        self.assertTrue(hasattr(suggestor, "ratings"), "ratings.pkl yüklenmedi!")
        self.assertLess(elapsed_time, 5, "Pickle yükleme süresi beklenenden uzun!")


# 🔹 2️⃣ Pickle Dosyalarının Yoksa Oluşturulma Testi
class TestNoExistingPickleFiles(unittest.TestCase):
    """Eğer pickle dosyaları yoksa, CSV dosyalarından oluşturulup oluşturulmadığını test eder."""

    def setUp(self):
        """Mevcut pickle dosyalarını silerek test ortamını sıfırlar."""
        if os.path.exists('OneriRobotu/archive/smd.pkl'):
            os.remove('OneriRobotu/archive/smd.pkl')
        if os.path.exists('OneriRobotu/archive/ratings.pkl'):
            os.remove('OneriRobotu/archive/ratings.pkl')

    def test_create_pickle_files(self):
        """Pickle dosyalarının yokken oluşturulup oluşturulmadığını test eder."""
        suggestor = Suggestor()
        self.assertTrue(os.path.exists('OneriRobotu/archive/smd.pkl'), "smd.pkl oluşturulmadı!")
        self.assertTrue(os.path.exists('OneriRobotu/archive/ratings.pkl'), "ratings.pkl oluşturulmadı!")

        with open('OneriRobotu/archive/smd.pkl', 'rb') as f:
            smd_data = pickle.load(f)
            self.assertIsInstance(smd_data, pd.DataFrame, "smd.pkl içeriği DataFrame olmalı!")
            self.assertGreater(len(smd_data), 0, "smd.pkl boş!")

        with open('OneriRobotu/archive/ratings.pkl', 'rb') as f:
            ratings_data = pickle.load(f)
            self.assertIsInstance(ratings_data, pd.DataFrame, "ratings.pkl içeriği DataFrame olmalı!")
            self.assertGreater(len(ratings_data), 0, "ratings.pkl boş!")

    def tearDown(self):
        """Test tamamlandıktan sonra oluşturulan pickle dosyalarını siler."""
        if os.path.exists('OneriRobotu/archive/smd.pkl'):
            os.remove('OneriRobotu/archive/smd.pkl')
        if os.path.exists('OneriRobotu/archive/ratings.pkl'):
            os.remove('OneriRobotu/archive/ratings.pkl')


# 🔹 3️⃣ Hybrid Metodunun Doğru Çalışma Testi (Geçerli Verilerle)
class TestHybridMethod(unittest.TestCase):
    """Hybrid metodunun geçerli girişlerle düzgün çalıştığını test eder."""

    def setUp(self):
        """Test için örnek film ve puan verilerini hazırlar."""
        self.input_data = {
            "input_1": "Inception", "rating_1": 5,
            "input_2": "The Matrix", "rating_2": 4,
            "input_3": "Interstellar", "rating_3": 5,
            "input_4": "The Dark Knight", "rating_4": 5,
            "input_5": "Gladiator"
        }
        self.suggestor = Suggestor(self.input_data)

    def test_hybrid_valid_inputs(self):
        """Hybrid metodunun beklenen sonucu üretip üretmediğini test eder."""
        recommendations = self.suggestor.hybrid(1, "Gladiator")
        self.assertIsInstance(recommendations, pd.DataFrame, "Çıktı bir DataFrame olmalı!")
        self.assertEqual(len(recommendations), 20, "Öneri listesi 20 film içermeli!")

        output_filename = "deneme_gelismis.xlsx"
        recommendations.to_excel(output_filename)
        self.assertTrue(os.path.exists(output_filename), "Çıktı dosyası oluşturulmalı!")

    def tearDown(self):
        """Test sonrası geçici dosyaları temizler."""
        output_filename = "deneme_gelismis.xlsx"
        if os.path.exists(output_filename):
            os.remove(output_filename)


# 🔹 4️⃣ Hybrid Metodunun Geçersiz Film İsimleriyle Testi
class TestHybridInvalidMovie(unittest.TestCase):
    """Geçersiz film isimleri girildiğinde sistemin nasıl tepki verdiğini test eder."""

    def setUp(self):
        """Geçersiz film isimleriyle test girişlerini hazırlar."""
        self.invalid_input = {
            "input_1": "ABCD1234",
            "rating_1": 3,
            "input_2": "XYZ5678",
            "rating_2": 2,
            "input_3": "FakeMovie1",
            "rating_3": 4,
            "input_4": "RandomFilm99",
            "rating_4": 5,
            "input_5": "Gladiator"
        }

    def test_hybrid_invalid_movie(self):
        """Geçersiz film isimleri girildiğinde hata verilip verilmediğini kontrol eder."""
        with self.assertRaises(SystemExit) as cm:
            Suggestor(self.invalid_input)
        self.assertEqual(cm.exception.code, 1, "Sistem çıkış kodu 1 olmalı, yani hata vermeli!")


# 🔹 5️⃣ Güvenlik Testi: SQL Injection ve Kötü Amaçlı Girişler
class TestSecurityCheck(unittest.TestCase):
    """Sistemin SQL Injection veya kötü niyetli girişlere karşı korunduğunu test eder."""

    def setUp(self):
        """Test için kötü niyetli girişleri hazırlar."""
        self.malicious_input = {
            "input_1": "DROP TABLE Movies;--",
            "rating_1": 3,
            "input_2": "' OR '1'='1",
            "rating_2": 5,
            "input_3": "<script>alert('Hacked');</script>",
            "rating_3": 4,
            "input_4": "Robert'); DROP TABLE Users;--",
            "rating_4": 2,
            "input_5": "Gladiator"
        }

    def test_security_check(self):
        """SQL Injection veya kötü amaçlı girişlerin engellenip engellenmediğini test eder."""
        try:
            suggestor = Suggestor(self.malicious_input)
            recommendations = suggestor.hybrid(1, "Gladiator")

            for bad_input in self.malicious_input.values():
                self.assertNotIn(bad_input, recommendations.values, "Kötü niyetli giriş öneri listesine sızmamalı!")

            output_file = "deneme_gelismis.xlsx"
            self.assertFalse(Path(output_file).exists(), "Kötü niyetli girişlerle dosya oluşturulmamalı!")

        except Exception as e:
            self.fail(f"Test sırasında beklenmedik bir hata oluştu: {e}")

if __name__ == "__main__":
    unittest.main()
