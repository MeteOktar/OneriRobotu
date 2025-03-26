import unittest
import os
import sys
import time
import pickle
import pandas as pd
from pathlib import Path
from Suggestor import Suggestor  # Öneri sisteminin ana kodu

# Pickle Dosyalarının Yüklenme Testi
class TestLoadingPickleFiles(unittest.TestCase):
    """Pickle dosyalarının düzgün yüklendiğini test eder"""

    def setUp(self):
        """Test öncesi pickle dosyalarının var olup olmadığını kontrol eder."""
        self.smd_path = Path("./archive/smd.pkl")
        self.ratings_path = Path("./archive/ratings.pkl")

    def test_loading_existing_pickles(self):
        """Pickle dosyaları varsa, CSV işlemleri atlanmalı ve hızlı yüklenmeli."""
        self.assertTrue(self.smd_path.is_file(), "smd.pkl bulunamadı!")
        self.assertTrue(self.ratings_path.is_file(), "ratings.pkl bulunamadı!")

        start_time = time.time()
        suggestor = Suggestor(None)
        elapsed_time = time.time() - start_time

        self.assertTrue(hasattr(suggestor, "smd"), "smd.pkl yüklenmedi!")
        self.assertTrue(hasattr(suggestor, "ratings"), "ratings.pkl yüklenmedi!")
        self.assertLess(elapsed_time, 5, "Pickle yükleme süresi beklenenden uzun!")


# Pickle Dosyalarının Yoksa Oluşturulma Testi
class TestNoExistingPickleFiles(unittest.TestCase):
    """Eğer pickle dosyaları yoksa, CSV dosyalarından oluşturulup oluşturulmadığını test eder."""

    def setUp(self):
        """Mevcut pickle dosyalarını silerek test ortamını sıfırlar."""
        if os.path.exists('./archive/smd.pkl'):
            os.remove('./archive/smd.pkl')
        if os.path.exists('./archive/ratings.pkl'):
            os.remove('./archive/ratings.pkl')

    def test_create_pickle_files(self):
        """Pickle dosyalarının yokken oluşturulup oluşturulmadığını test eder."""
        suggestor = Suggestor(None)
        self.assertTrue(os.path.exists('./archive/smd.pkl'), "smd.pkl oluşturulmadı!")
        self.assertTrue(os.path.exists('./archive/ratings.pkl'), "ratings.pkl oluşturulmadı!")

        with open('./archive/smd.pkl', 'rb') as f:
            smd_data = pickle.load(f)
            self.assertIsInstance(smd_data, pd.DataFrame, "smd.pkl içeriği DataFrame olmalı!")
            self.assertGreater(len(smd_data), 0, "smd.pkl boş!")

        with open('./archive/ratings.pkl', 'rb') as f:
            ratings_data = pickle.load(f)
            self.assertIsInstance(ratings_data, pd.DataFrame, "ratings.pkl içeriği DataFrame olmalı!")
            self.assertGreater(len(ratings_data), 0, "ratings.pkl boş!")

    def tearDown(self):
        """Test tamamlandıktan sonra oluşturulan pickle dosyalarını siler."""
        if os.path.exists('./archive/smd.pkl'):
            os.remove('./archive/smd.pkl')
        if os.path.exists('./archive/ratings.pkl'):
            os.remove('./archive/ratings.pkl')


# Hybrid Metodunun Doğru Çalışma Testi (Geçerli Verilerle)
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


# Hybrid Metodunun Geçersiz Film İsimleriyle Testi
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
            "input_5": "terduydr"
        }

    def test_hybrid_invalid_movie(self):
        """Geçersiz film isimleri girildiğinde hata verilip verilmediğini kontrol eder."""
        with self.assertRaises(SystemExit) as cm:
            Suggestor(self.invalid_input)
        self.assertEqual(cm.exception.code, 1, "Sistem çıkış kodu 1 olmalı, yani hata vermeli!")

class TestSuggestorMethods(unittest.TestCase):
    """Suggestor sınıfındaki metodları test eder."""

    def setUp(self):
        """Test için Suggestor örneğini hazırlar."""
        self.suggestor = Suggestor(None)

    def test_clean_data(self):
        """clean_data metodunun film ismi üzerindeki işlemi doğru yaptığını test eder."""
        # Film ismini doğru şekilde temizlemesi gerekiyor
        self.assertEqual(self.suggestor.clean_data("Tom Cruise"), "tomcruise")  # Boşluklar kaldırılacak ve küçük harfe çevrilecek
        self.assertEqual(self.suggestor.clean_data("The Matrix"), "thematrix")  # Yine küçük harfe ve boşluksuz olacak
        self.assertEqual(self.suggestor.clean_data("Avatar: The Way of Water"), "avatar:thewayofwater")  # Boşluklar ve büyük harfler kaldırılacak

    def test_get_director(self):
        """get_director metodunun yönetmeni doğru çektiğini test eder"""
        crew = [{"job": "Director", "name": "Christopher Nolan"}, {"job": "Producer", "name": "Emma Thomas"}]
        self.assertEqual(self.suggestor.get_director(crew), "Christopher Nolan")

    def test_get_list(self):
        """get_list metodunun en fazla 3 eleman döndürdüğünü test eder"""
        keywords = [{"name": "sci-fi"}, {"name": "thriller"}, {"name": "drama"}, {"name": "action"}]
        self.assertEqual(self.suggestor.get_list(keywords), ["sci-fi", "thriller", "drama"])

    def test_create_soup(self):
        """create_soup metodunun kelimeleri birleştirdiğini test eder"""
        row = {"keywords": ["sci-fi", "thriller"], "cast": ["Tom Hardy", "Cillian Murphy"], "director": "Nolan", "genres": ["Action", "Drama"]}
        self.assertEqual(self.suggestor.create_soup(row), "sci-fi thriller Tom Hardy Cillian Murphy Nolan Action Drama")

# Güvenlik Testi: SQL Injection ve Kötü Amaçlı Girişler
class TestSecurityCheck(unittest.TestCase):
    """Sistemin SQL Injection veya kötü niyetli girişlere karşı korunduğunu test eder."""

    def setUp(self):
        """Test için kötü niyetli girişleri hazırlar."""
        self.malicious_input = {
            "input_1": "DROP TABLE Movies",
            "rating_1": 3,
            "input_2": "' ORfxgjh",
            "rating_2": 5,
            "input_3": "<script>alertHackedscript>",
            "rating_3": 4,
            "input_4": "Robert'); DROP TABLE Users;--",
            "rating_4": 2,
            "input_5": "w54e6dr5f7t6g8yhuj"
        }
    
    def test_security_check(self):
        """SQL Injection veya kötü amaçlı girişlerin engellenip engellenmediğini test eder."""
        try:
            suggestor = Suggestor(self.malicious_input)
            recommendations = suggestor.hybrid(1, "Gladiator")

            for bad_input in self.malicious_input.values():
                self.assertNotIn(bad_input, recommendations.values, "Kötü niyetli giriş öneri listesine sızmamalı!")

            output_file = "output.xlsx"
            self.assertFalse(Path(output_file).exists(), "Kötü niyetli girişlerle dosya oluşturulmamalı!")

        except Exception as e:
            self.fail(f"Test sırasında beklenmedik bir hata oluştu: {e}")

# Verilen testler için yeni test sınıfı


if __name__ == "__main__":
    # Testlerin çıktısını log dosyasına yazdırmak için TextTestRunner'ı kullan
    with open("./testLogs.txt", 'w') as log:
        runner = unittest.TextTestRunner(stream=log)
        unittest.main(testRunner=runner, exit=False)

    # Son olarak, sys.stdout'u eski haline getirme
    sys.stdout = sys.__stdout__
