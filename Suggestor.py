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
    def __init__(self):
        start_time = time.time()
        # CSV dosyalarini yukle
        smdpickle_path = Path("OneriRobotu/archive/smd.pkl")
        ratingpickle_path = Path("OneriRobotu/archive/ratings.pkl")
        if smdpickle_path.is_file():
            self.smd = pd.read_pickle("OneriRobotu/archive/smd.pkl")
            print("--- %s SMD_PICKLE OKUDU seconds ---" % (time.time() - start_time))
        else:
            #burayi ileride ayri bir fonksiyon olarak yapmak lazim
            start_time = time.time()
            self.md = pd.read_csv('OneriRobotu/archive/movies_metadata.csv')
            self.credits = pd.read_csv('OneriRobotu/archive/credits.csv')
            self.keywords = pd.read_csv('OneriRobotu/archive/keywords.csv')
            self.links_small = pd.read_csv('OneriRobotu/archive/links_small.csv')
            
            """
            User profiling icin: input almaya basladigimizda user title girecek, biz title'i autocomplete ile
            tamamlayacagiz sonra rating girecek. 
            db'den title'i kullanarak id cekecegiz. sonra self.rows kismina [1,id,rating] seklinde yerlestirecegiz.
            inputlar bittikten sonra son bir film alip (su filme benzer filmleri goster)
            o filme benzer filmleri kullanicinin rating profiline gore siralayacak ve output edecek.
            
            veya direkt user profiling kismindan sonra you might also like diyip son film almadan da liste verebiliriz
            """
            """ 
            self.fields = ['userId', 'movieId', 'rating']
            self.rows = [[1,31,5],[1,1029,3],[1,1061,3],[1,1129,2]]
            self.filename = "OneriRobotu/archive/userRatings.csv"
            with open (self.filename,"w") as csvfile:
                csvwriter = csvwriter(csvfile)
                csvwriter.writerow(self.fields)
                csvwriter.writerows(self.rows)
            self.usercsv = pd.read_csv(self.filename)"""
            
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
            self.smd.to_pickle("OneriRobotu/archive/smd.pkl")
            
        if(ratingpickle_path.is_file()):
            start_time = time.time()
            self.ratings = pd.read_pickle("OneriRobotu/archive/ratings.pkl")
            print("--- %s PICKLE_RATING OKUDU seconds ---" % (time.time() - start_time))
        else:
            self.ratings = pd.read_csv('OneriRobotu/archive/ratings_small.csv')
            self.ratings.to_pickle("OneriRobotu/archive/ratings.pkl")
        
        
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
        
        # Surprise kutuphanesi ile SVD modelini egit
        start_time = time.time()
        reader = Reader()
        data = Dataset.load_from_df(self.ratings[['userId', 'movieId', 'rating']], reader)
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
        
        # id_map ve indices_map'i olustur
        start_time = time.time()
        id_map = pd.read_csv("OneriRobotu/archive/links_small.csv")[['movieId', 'tmdbId']]
        id_map['tmdbId'] = id_map['tmdbId'].apply(self.convert_int)
        id_map.columns = ['movieId', 'id']
        id_map = id_map.merge(self.smd[['title', 'id']], on='id').set_index('title')
        self.id_map = id_map
        indices_map = id_map.set_index('id')
        indices_map.index = indices_map.index.astype(int)
        self.indices_map = indices_map
        print("--- %s ID VE INDEX MAP seconds ---" % (time.time() - start_time))
        
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
if __name__ == "__main__":
    start_time = time.time()
    suggestor = Suggestor()
    recommendations = suggestor.hybrid(312, 'Interstellar')
    recommendations.to_excel("deneme.xlsx")
    print("--- %s seconds ---" % (time.time() - start_time))
