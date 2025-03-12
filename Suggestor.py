import pandas as pd
import numpy as np
import csv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ast import literal_eval
from surprise import Reader, Dataset, model_selection, SVD
import time
from pathlib import Path
class Suggestor:
    def __init__(self, input):
        start_time = time.time()
        # CSV dosyalarini yukle
        smdpickle_path = Path("./archive/smd.pkl")
        ratingpickle_path = Path("./archive/ratings.pkl")
        if smdpickle_path.is_file():
            self.smd = pd.read_pickle("./archive/smd.pkl")
            print("--- %s SMD_PICKLE OKUDU seconds ---" % (time.time() - start_time))
        else:
            #burayi ileride ayri bir fonksiyon olarak yapmak lazim
            start_time = time.time()
            self.md = pd.read_csv('./archive/movies_metadata.csv')
            self.credits = pd.read_csv('./archive/credits.csv')
            self.keywords = pd.read_csv('./archive/keywords.csv')
            self.links_small = pd.read_csv('./archive/links_small.csv')
            
            """
            User profiling icin: input almaya basladigimizda user title girecek, biz title'i autocomplete ile
            tamamlayacagiz sonra rating girecek. 
            db'den title'i kullanarak id cekecegiz. sonra self.rows kismina [1,id,rating] seklinde yerlestirecegiz.
            inputlar bittikten sonra son bir film alip (su filme benzer filmleri goster)
            o filme benzer filmleri kullanicinin rating profiline gore siralayacak ve output edecek.
            
            veya direkt user profiling kismindan sonra you might also like diyip son film almadan da liste verebiliriz
            """
            
            # Gerekli sutunlari donustur ve yil sutunu olustur
            vote_counts = self.md[self.md['vote_count'].notnull()]['vote_count'].astype('int')
            vote_averages = self.md[self.md['vote_average'].notnull()]['vote_average'].astype('int')
            self.md['year'] = pd.to_datetime(self.md['release_date'], errors='coerce').apply(
                lambda x: str(x).split('-')[0] if x != np.nan else np.nan)
            m = vote_counts.quantile(0.95)
            C = vote_averages.mean()
            
            # links_small dosyasindaki tmdbId degerlerini filtrele
            self.links_small = self.links_small[self.links_small['tmdbId'].notnull()]['tmdbId'].astype('int')
            # Belirli satirlari kaldir (hatali veriler)
            self.md = self.md.drop([19730, 29503, 35587])
            
            # Veri tiplerini ayarla
            self.keywords['id'] = self.keywords['id'].astype('int')
            self.credits['id'] = self.credits['id'].astype('int')
            self.md['id'] = self.md['id'].astype('int')
            
            # credits ve keywords dosyalarini md ile birlestir
            self.md = self.md.merge(self.credits, on='id')
            self.md = self.md.merge(self.keywords, on='id')
            
            # Filtre: links_small icindeki id'lere sahip verileri al (smd)
            self.smd = self.md[self.md['id'].isin(self.links_small)]
            self.smd = self.smd.copy()
            
            # Literal evaluation islemi: 'cast', 'crew', 'keywords', 'genres'
            features = ['cast', 'crew', 'keywords', 'genres']
            for feature in features:
                self.smd[feature] = self.smd[feature].apply(literal_eval)
            
            # 'director' sutununu olustur: crew bilgisinden
            self.smd['director'] = self.smd['crew'].apply(self.get_director)
            
            # 'cast', 'keywords', 'genres' sutunlarini listeye cevir
            features_list = ['cast', 'keywords', 'genres']
            for feature in features_list:
                self.smd[feature] = self.smd[feature].apply(self.get_list)
            
            # Ek sutunlar: cast_size, crew_size
            self.smd['cast_size'] = self.smd['cast'].apply(lambda x: len(x))
            self.smd['crew_size'] = self.smd['crew'].apply(lambda x: len(x))
            
            # Belirli sutunlari temizle (ornegin "Tom Cruise" -> "tomcruise")
            features_clean = ['cast', 'keywords', 'director', 'genres']
            for feature in features_clean:
                self.smd[feature] = self.smd[feature].apply(self.clean_data)
            
            # 'soup' sutununu olustur: oneriler icin metin birlestirme
            self.smd['soup'] = self.smd.apply(self.create_soup, axis=1)
            print("--- %s CORBA YAPTI seconds ---" % (time.time() - start_time))
            self.smd.to_pickle("./archive/smd.pkl")
            
        if(ratingpickle_path.is_file()):
            start_time = time.time()
            self.ratings = pd.read_pickle("./archive/ratings.pkl")
            print("--- %s PICKLE_RATING OKUDU seconds ---" % (time.time() - start_time))
        else:
            self.ratings = pd.read_csv('./archive/ratings_small.csv')
            self.ratings.to_pickle("./archive/ratings.pkl")
        
        
        # CountVectorizer ve cosine similarity hesaplamalari
        start_time = time.time()
        count = CountVectorizer(stop_words='english')
        count_matrix = count.fit_transform(self.smd['soup'])
        self.cosine_sim = cosine_similarity(count_matrix, count_matrix)
        print("--- %s COUNT VECTORIZER seconds ---" % (time.time() - start_time))
        
        # Indeksleri ayarla
        start_time = time.time()
        self.smd = self.smd.reset_index()
        self.titles = self.smd['title']
        self.indices = pd.Series(self.smd.index, index=self.smd['title'])
        print("--- %s INDEXLERI AYARLADI seconds ---" % (time.time() - start_time))
        
#------------------------------------------------------------------------------------------------------------------------- 
        # id_map ve indices_map'i olustur
        start_time = time.time()
        id_map = pd.read_csv("./archive/links_small.csv")[['movieId', 'tmdbId']]
        id_map['tmdbId'] = id_map['tmdbId'].apply(self.convert_int)
        id_map.columns = ['movieId', 'id']
        id_map = id_map.merge(self.smd[['title', 'id']], on='id').set_index('title')
        self.id_map = id_map
        indices_map = id_map.set_index('id')
        indices_map.index = indices_map.index.astype(int)
        self.indices_map = indices_map
        print("--- %s ID VE INDEX MAP seconds ---" % (time.time() - start_time))
    
        # Film isimlerini küçük harfe çevirerek indeks oluştur
        id_map.index = id_map.index.str.lower()

        # Kullanıcıdan gelen inputları küçük harfe çevir
        input = {key: value.lower() for key, value in input.items()}

        # Sadece film isimlerini al
        movie_inputs = {key: value.lower() for key, value in input.items() if key.startswith("input_")}

        # Film isimlerine karşılık gelen id'leri al
        movie_ids = []
        for movie_name in movie_inputs.values():
            if movie_name in id_map.index:
                movie_id = id_map.loc[movie_name, 'id']
                movie_ids.append(movie_id)
            else:
                movie_ids.append(None)  # Eğer film ismi eşleşmezse None eklenir

        # Hata: movie_ids ve movie_inputs.values() farklı uzunluktaysa bunu önlemek için liste boyutunu kontrol et
        if len(movie_inputs) != len(movie_ids):
            print("Uyarı: movie_inputs ve movie_ids uzunlukları eşleşmiyor!")
            print(f"movie_inputs: {len(movie_inputs)}, movie_ids: {len(movie_ids)}")

        # Eşleşmeyen filmleri kontrol et
        missing_movies = [movie for i, movie in enumerate(movie_inputs.values()) if i < len(movie_ids) and movie_ids[i] is None]
        if missing_movies:
            print("Eşleşmeyen filmler:", missing_movies)

        # self.rows listesini oluştur
        self.fields = ['userId', 'movieId', 'rating']
        self.rows = [[1, movie_id, input[f'rating_{i+1}']] for i, movie_id in enumerate(movie_ids) if movie_id is not None]
        self.filename = "./archive/userRatings.csv"
        with open(self.filename, "w", newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(self.fields)
            csvwriter.writerows(self.rows)
        self.usercsv = pd.read_csv(self.filename)
#-------------------------------------------------------------------------------------------------------------------------
        
        # Surprise kutuphanesi ile SVD modelini egit
        start_time = time.time()
        reader = Reader()
        data = Dataset.load_from_df(self.usercsv[['userId', 'movieId', 'rating']], reader)
        print("--- %s DATASET seconds ---" % (time.time() - start_time))
        
        """
        DAHA BUYUK DATASET KULLANILDIGINDA CROSS VALIDATE ILE DOGRU MU CALISIYO BAK
        
        start_time = time.time()
        print(model_selection.cross_validate(self.svd, data, measures=['RMSE', 'MAE']))
        print("--- %s CROSS VALIDATE seconds ---" % (time.time() - start_time))
        """
        self.svd = SVD()
        start_time= time.time()
        trainset = data.build_full_trainset()
        print("--- %s BUILD FULL TRAINSET seconds ---" % (time.time() - start_time))
        
        start_time = time.time()
        self.svd.fit(trainset)
        print("--- %s SVD TRAIN seconds ---" % (time.time() - start_time))
        
        # # id_map ve indices_map'i olustur
        # start_time = time.time()
        # id_map = pd.read_csv("./archive/links_small.csv")[['movieId', 'tmdbId']]
        # id_map['tmdbId'] = id_map['tmdbId'].apply(self.convert_int)
        # id_map.columns = ['movieId', 'id']
        # id_map = id_map.merge(self.smd[['title', 'id']], on='id').set_index('title') # ONCEKI ID_MAP YERI
        # self.id_map = id_map
        # indices_map = id_map.set_index('id')
        # indices_map.index = indices_map.index.astype(int)
        # self.indices_map = indices_map
        # print("--- %s ID VE INDEX MAP seconds ---" % (time.time() - start_time))
        
        # Debug amacli Excel ciktilari
        #self.indices_map.to_excel("indexler.xlsx")
        #self.id_map.to_excel("idler.xlsx")
    
    # Yardimci metodlar:
    def clean_data(self, x):
        if isinstance(x, list):
            return [str.lower(i.replace(" ", "")) for i in x]
        else:
            if isinstance(x, str):
                return str.lower(x.replace(" ", ""))
            else:
                return ''
    
    def get_list(self, x):
        if isinstance(x, list):
            names = [i['name'] for i in x]
            return names[:3] if len(names) > 3 else names
        return []
    
    def get_director(self, x):
        for i in x:
            if i['job'] == 'Director':
                return i['name']
        return np.nan
    
    def create_soup(self, x):
        return ' '.join(x['keywords']) + ' ' + ' '.join(x['cast']) + ' ' + x['director'] + ' ' + ' '.join(x['genres'])
    
    def convert_int(self, x):
        try:
            return int(x)
        except:
            return np.nan
    
    def hybrid(self, userId, title):
        """
        Kullanici ve film basligina gore hibrit oneri listesi olusturur.
        Ilk olarak cosine similarity ile benzer filmler belirlenir,
        ardindan SVD modelinin tahmin puanlarina gore siralanir.
        """
        start_time = time.time()
        idx = self.indices[title]
        
        # Cosine similarity skorlarini hesapla ve ilk 25 benzer filmi al
        sim_scores = list(enumerate(self.cosine_sim[int(idx)]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:26]
        movie_indices = [i[0] for i in sim_scores]
        
        movies = self.smd.iloc[movie_indices][['title', 'vote_count', 'vote_average', 'year', 'id']]
        # SVD modelinin tahmin ettigi puanlari hesapla
        movies['est'] = movies['id'].apply(
            lambda x: self.svd.predict(userId, self.indices_map.loc[x]['movieId']).est)
        movies = movies.sort_values('est', ascending=False)
        print("--- %s HYBRID seconds ---" % (time.time() - start_time))
        return movies.head(20)
        

# Dosya dogrudan calisirken buradan calisiyor
# if __name__ == "__main__":
#     start_time = time.time()
#     suggestor = Suggestor(data)
#     recommendations = suggestor.hybrid(312, 'Gladiator')
#     recommendations.to_excel("deneme.xlsx")
#     print("--- %s seconds ---" % (time.time() - start_time))
