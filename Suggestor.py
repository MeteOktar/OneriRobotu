import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from ast import literal_eval
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Reader, Dataset, model_selection,SVD


class Suggestor:
    def __init__(self):
        
        self.df1 = pd.read_csv("OneriRobotu/archive/tmdb_5000_credits.csv") #movie_id, title, cast, crew
        self.df2 = pd.read_csv("OneriRobotu/archive/tmdb_5000_movies.csv")  #budget, genres, homepage, id, keywords, 
        #original_language, original_title, overview, popularity, production_companies, production_countries, 
        # release_date, revenue, runtime, spoken_languages, status, tagline, title, vote_average, vote_count
        self.df1.columns = ['id','tittle','cast','crew']
        self.df2= self.df2.merge(self.df1,on='id')
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.df2['overview'] = self.df2['overview'].fillna('')
        self.tfidf_matrix = self.tfidf.fit_transform(self.df2['overview'])
        
        
        
    def get_director(self,x):
        for i in x:
            if i['job'] == 'Director':
                return i['name']
        return np.nan
    def get_list(self,x):
        if isinstance(x, list):
            names = [i['name'] for i in x]
            #Check if more than 3 elements exist. If yes, return only first three. If no, return entire list.
            if len(names) > 3:
                names = names[:3]
            return names
        #Return empty list in case of missing/malformed data
        return []
    def clean_data(self,x):
        if isinstance(x, list):
            return [str.lower(i.replace(" ", "")) for i in x]
        else:
            #Check if director exists. If not, return empty string
            if isinstance(x, str):
                return str.lower(x.replace(" ", ""))
            else:
                return ''        
    def create_soup(self,x):
        return ' '.join(x['keywords']) + ' ' + ' '.join(x['cast']) + ' ' + x['director'] + ' ' + ' '.join(x['genres'])
    
    def get_recommendations(self,title):
        
        
        features = ['cast','crew','keywords','genres']
        for feature in features:
            self.df2[feature] = self.df2[feature].apply(literal_eval)
            
        #director'u alir
        self.df2['director'] = self.df2['crew'].apply(self.get_director)
        
        features = ['cast', 'keywords', 'genres']
        for feature in features:
            self.df2[feature] = self.df2[feature].apply(self.get_list)
            
        #veriyi temizler ornek: "Tom Cruise" -> "tomcruise"
        features = ['cast', 'keywords', 'director', 'genres']
        for feature in features:
            self.df2[feature] = self.df2[feature].apply(self.clean_data)
        
        self.df2['soup'] = self.df2.apply(self.create_soup, axis=1)
        
        count = CountVectorizer(stop_words='english')
        count_matrix = count.fit_transform(self.df2['soup'])
        
        #metadata based recommendation
        cosine_sim = cosine_similarity(count_matrix, count_matrix)
        
        #plot benzerligine gore recommendation icin
        #cosine_simPlot = linear_kernel(self.tfidf_matrix, self.tfidf_matrix)
        
        self.df2 = self.df2.reset_index()
        indices = pd.Series(self.df2.index, index=self.df2['title']).drop_duplicates()
        
        
        
        idx = indices[title]
        #pairwise similarity skorlarini alir
        sim_scores = list(enumerate(cosine_sim[idx]))
        #benzerlik skorlarini siralar
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        #ilk 10 filmden olusan bir liste olusturur
        sim_scores = sim_scores[1:11]
        #filmlerin indexlerini alir, df2'den bulmak icin
        movie_indicex = [i[0] for i in sim_scores]
        #en benzer ilk 10 filmi doner
        
        
        
        #----------------COLLABORATIVE------------------
       
        
        return self.df2['title'].iloc[movie_indicex]
        
suggest = Suggestor()    
#suggest.get_recommendations("No Country for Old Men").to_excel("deneme.xlsx")
reader = Reader()
ratings = pd.read_csv("OneriRobotu/archive/ratings_small.csv")
data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
svd = SVD()
model_selection.cross_validate(svd, data, measures=['RMSE','MAE'])
trainset = data.build_full_trainset()
svd.fit(trainset)
ratings[ratings['userId'] == 1].to_excel("deneme.xlsx")
print(svd.predict(1, 302, 3))

