"""1- hiçbir şey yoksa
2- izlediği filmleri tekrar öneriyor mu
3-önerdiği şeyi tekrar öneriyor mu
4-puan vericek izleidkten sonra verdi mi vermedi mi
5-kullanıcı gözünden girşi  yapolıdı mı video
6- yazılan fonsiyonlari test
7- kullanıcı bilgileri test kısmı"""
from Suggestor import Suggestor

suggestor_Test = Suggestor()

verilen_cikti = Suggestor.clean_data("pirates of the caribbean")
beklenen_cikti = 'piratesofthecaribbean'

if beklenen_cikti == verilen_cikti:
    print("Çıktı doğru, metot doğru çalışıyor.")
else:
    print("Çıktı yanlış, metot doğru çalışmıyor.")





verilen_cikti_2 = Suggestor.get_director("pirates of the caribbean")
beklenen_cikti_2 = 'Espen Sandberg'

if beklenen_cikti_2 == verilen_cikti_2:
    print("Çıktı doğru, metot doğru çalışıyor.")
else:
    print("Çıktı yanlış, metot doğru çalışmıyor.")



"""" kıyas için  iki defa yazılacak userid ve title
suggestor = Suggestor()
recommendations_list_verilen = suggestor.hybrid(userId, title).values.tolist()
recommendations_list_karşılaştırma = suggestor.hybrid(userId, title).values.tolist()





print("Farklı Filmler:", differences)
"""

""""
import unittest
from pathlib import Path
import time
from dosya adı import Suggestor  # your_module'ü kendi dosya adınla değiştir

class TestLoadingPickleFiles(unittest.TestCase):
    def setUp(self):
        """ """Test öncesi pickle dosyalarının var olup olmadığını kontrol eder. """ """
        self.smd_path = Path("OneriRobotu/archive/smd.pkl")
        self.ratings_path = Path("OneriRobotu/archive/ratings.pkl")

    def test_loading_existing_pickles(self):
        """ """Pickle dosyaları varsa, CSV birleşme adımları atlanmalı."""""""
        
        # Ön Koşul: Pickle dosyalarının mevcut olması gerekiyor
        self.assertTrue(self.smd_path.is_file(), "smd.pkl bulunamadı!")
        self.assertTrue(self.ratings_path.is_file(), "ratings.pkl bulunamadı!")
        
        # 1. Suggestor sınıfını başlat
        start_time = time.time()
        suggestor = Suggestor()
        elapsed_time = time.time() - start_time

        # 2. CSV işlemlerini atlayıp atlamadığını kontrol et
        self.assertTrue(hasattr(suggestor, "smd"), "smd.pkl yüklenmedi!")
        self.assertTrue(hasattr(suggestor, "ratings"), "ratings.pkl yüklenmedi!")
        
        # Performans testi: Verinin hızlı yüklenmesi bekleniyor (örnek olarak 5 saniye sınır koyduk)
        self.assertLess(elapsed_time, 5, "Pickle yükleme süresi beklenenden uzun!")
        
        print("Test Passed: Pickle files loaded successfully without CSV processing.")

if __name__ == "__main__":
    unittest.main()

"""
"""
import unittest
import os
import pickle
from pathlib import Path
import pandas as pd
from suggestor import Suggestor  # Suggestor sınıfını içeri aktarıyoruz

class TestSuggestor(unittest.TestCase):
    
    def setUp(self):
        # Öncelikle mevcut pickle dosyalarını sil
        if os.path.exists('OneriRobotu/archive/smd.pkl'):
            os.remove('OneriRobotu/archive/smd.pkl')
        if os.path.exists('OneriRobotu/archive/ratings.pkl'):
            os.remove('OneriRobotu/archive/ratings.pkl')

    def test_no_existing_pickle_files(self):
        # Suggestor sınıfını başlat
        suggestor = Suggestor()
        
        # CSV dosyaları birleştirildi mi kontrol et
        suggestor.smd = pd.read_pickle('OneriRobotu/archive/smd.pkl')
        suggestor.ratings = pd.read_pickle('OneriRobotu/archive/ratings.pkl')
        
        # Beklenen sonuçlar: Pickle dosyaları başarılı bir şekilde oluşturulmuş olmalı
        self.assertTrue(os.path.exists('OneriRobotu/archive/smd.pkl'), "smd.pkl dosyası oluşturulmadı")
        self.assertTrue(os.path.exists('OneriRobotu/archive/ratings.pkl'), "ratings.pkl dosyası oluşturulmadı")

        # smd.pkl dosyasının veri yapısını kontrol et
        with open('OneriRobotu/archive/smd.pkl', 'rb') as f:
            smd_data = pickle.load(f)
            self.assertIsInstance(smd_data, pd.DataFrame, "smd.pkl içeriği DataFrame değil")
            self.assertGreater(len(smd_data), 0, "smd.pkl boş")

        # ratings.pkl dosyasının veri yapısını kontrol et
        with open('OneriRobotu/archive/ratings.pkl', 'rb') as f:
            ratings_data = pickle.load(f)
            self.assertIsInstance(ratings_data, pd.DataFrame, "ratings.pkl içeriği DataFrame değil")
            self.assertGreater(len(ratings_data), 0, "ratings.pkl boş")
    
    def tearDown(self):
        # Test sonrasında pickle dosyalarını sil
        if os.path.exists('OneriRobotu/archive/smd.pkl'):
            os.remove('OneriRobotu/archive/smd.pkl')
        if os.path.exists('OneriRobotu/archive/ratings.pkl'):
            os.remove('OneriRobotu/archive/ratings.pkl')


if __name__ == "__main__":
    unittest.main()


"""


