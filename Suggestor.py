import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from ast import literal_eval
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
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
#suggest = Suggestor()    
#suggest.get_recommendations("No Country for Old Men").to_excel("deneme.xlsx")



def clean_data(x):
        if isinstance(x, list):
            return [str.lower(i.replace(" ", "")) for i in x]
        else:
            #Check if director exists. If not, return empty string
            if isinstance(x, str):
                return str.lower(x.replace(" ", ""))
            else:
                return ''

def get_list(x):
    if isinstance(x, list):
        names = [i['name'] for i in x]
        #Check if more than 3 elements exist. If yes, return only first three. If no, return entire list.
        if len(names) > 3:
            names = names[:3]
        return names
    #Return empty list in case of missing/malformed data
    return []
def get_director(x):
    for i in x:
        if i['job'] == 'Director':
            return i['name']
    return np.nan

def create_soup(x):
        return ' '.join(x['keywords']) + ' ' + ' '.join(x['cast']) + ' ' + x['director'] + ' ' + ' '.join(x['genres'])



md = pd.read_csv('OneriRobotu/archive/movies_metadata.csv')
credits = pd.read_csv('OneriRobotu/archive/credits.csv')
keywords = pd.read_csv('OneriRobotu/archive/keywords.csv')
links_small = pd.read_csv('OneriRobotu/archive/links_small.csv')
ratings = pd.read_csv("OneriRobotu/archive/ratings_small.csv")

vote_counts = md[md['vote_count'].notnull()]['vote_count'].astype('int')
vote_averages = md[md['vote_average'].notnull()]['vote_average'].astype('int')
md['year'] = pd.to_datetime(md['release_date'], errors='coerce').apply(lambda x: str(x).split('-')[0] if x != np.nan else np.nan)
m = vote_counts.quantile(0.95)
C = vote_averages.mean()


links_small = links_small[links_small['tmdbId'].notnull()]['tmdbId'].astype('int')
md = md.drop([19730, 29503, 35587])

keywords['id'] = keywords['id'].astype('int')
credits['id'] = credits['id'].astype('int')
md['id'] = md['id'].astype('int')

md = md.merge(credits, on='id')
md = md.merge(keywords, on='id')

smd = md[md['id'].isin(links_small)]
smd = smd.copy()
print(smd.shape)

features = ['cast','crew','keywords','genres']
for feature in features:
    smd[feature] = smd[feature].apply(literal_eval)

smd['director'] = smd['crew'].apply(get_director)

features = ['cast', 'keywords', 'genres']
for feature in features:
    smd[feature] = smd[feature].apply(get_list)

smd['cast_size'] = smd['cast'].apply(lambda x: len(x))
smd['crew_size'] = smd['crew'].apply(lambda x: len(x))

#veriyi temizler ornek: "Tom Cruise" -> "tomcruise"
features = ['cast', 'keywords', 'director', 'genres']
for feature in features:
    smd[feature] = smd[feature].apply(clean_data)

s = smd.apply(lambda x: pd.Series(x['keywords']),axis=1).stack().reset_index(level=1, drop=True)
s.name = 'keyword'

s = s.value_counts()
s = s[s > 1]
stemmer = SnowballStemmer('english')

smd['soup'] = smd.apply(create_soup, axis=1)

count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(smd['soup'])

cosine_sim = cosine_similarity(count_matrix, count_matrix)

smd = smd.reset_index()
titles = smd['title']
indices = pd.Series(smd.index, index=smd['title'])

reader = Reader()

data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
svd = SVD()
model_selection.cross_validate(svd, data, measures=['RMSE','MAE'])
trainset = data.build_full_trainset()
svd.fit(trainset)

def convert_int(x):
    try:
        return int(x)
    except:
        return np.nan
    
id_map = pd.read_csv("OneriRobotu/archive/links_small.csv")[['movieId', 'tmdbId']]
id_map['tmdbId'] = id_map['tmdbId'].apply(convert_int)
id_map.columns = ['movieId', 'id']
id_map = id_map.merge(smd[['title', 'id']], on='id').set_index('title')
indices_map = id_map.set_index('id')
indices_map.index = indices_map.index.astype(int)

indices_map.to_excel("indexler.xlsx")  # Tüm index değerlerini listele
id_map.to_excel("idler.xlsx")  # Tüm id değerlerini listele



def hybrid(userId, title):
    idx = indices[title]
    tmdbId = id_map.loc[title]['id']
    #print(idx)
    movie_id = id_map.loc[title]['movieId']
    
    sim_scores = list(enumerate(cosine_sim[int(idx)]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:26]
    movie_indices = [i[0] for i in sim_scores]
    
    movies = smd.iloc[movie_indices][['title', 'vote_count', 'vote_average', 'year', 'id']]
    movies['est'] = movies['id'].apply(lambda x: svd.predict(userId, indices_map.loc[x]['movieId']).est)
    movies = movies.sort_values('est', ascending=False)
    return movies.head(20)

hybrid(1,'No Country for Old Men').to_excel("deneme.xlsx")

