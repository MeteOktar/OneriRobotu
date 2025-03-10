import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
df1 = pd.read_csv("OneriRobotu/archive/tmdb_5000_credits.csv") #movie_id, title, cast, crew
df2 = pd.read_csv("OneriRobotu/archive/tmdb_5000_movies.csv")  #budget, genres, homepage, id, keywords, 
#original_language, original_title, overview, popularity, production_companies, production_countries, 
# release_date, revenue, runtime, spoken_languages, status, tagline, title, vote_average, vote_count
df1.columns = ['id','tittle','cast','crew']
df2= df2.merge(df1,on='id')
f = open("deneme.xlsx","w")
#ingilizcedeki gereksiz kelimeleri(the a is in for...) çıkartır ve tf-idf hesaplar
#tf-idf: bir belgedeki bir kelimenin önemini belirler
#tf: bir kelimenin bir belgedeki frekansı
#idf: bir kelimenin tüm belgelerdeki frekansı
tfidf = TfidfVectorizer(stop_words='english')
#NaN değerleri boş string ile doldurur
df2['overview'] = df2['overview'].fillna('')
#tf-idf matrisini oluşturur
tfidf_matrix = tfidf.fit_transform(df2['overview'])
#linear_kernel kullanmamizin sebebi cosine_similarities()'den hizli olmasidir
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
#title vererek index bulmamiza yarayacak bir pandas serisi olusturur
indices = pd.Series(df2.index, index=df2['title']).drop_duplicates()

def get_recommendatitons(title, cosine_sim=cosine_sim):
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
    return df2['title'].iloc[movie_indicex]
get_recommendatitons("The Avengers").to_excel("deneme.xlsx")