#!/usr/bin/env python
# coding: utf-8

# # Desafio 6
# 
# Neste desafio, vamos praticar _feature engineering_, um dos processos mais importantes e trabalhosos de ML. Utilizaremos o _data set_ [Countries of the world](https://www.kaggle.com/fernandol/countries-of-the-world), que contém dados sobre os 227 países do mundo com informações sobre tamanho da população, área, imigração e setores de produção.
# 
# > Obs.: Por favor, não modifique o nome das funções de resposta.

# ## _Setup_ geral

# In[1]:


import pandas as pd
import numpy as np
import seaborn as sns
import sklearn as sk
from sklearn.preprocessing import KBinsDiscretizer, OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


# In[2]:


# Algumas configurações para o matplotlib.
# %matplotlib inline

from IPython.core.pylabtools import figsize


figsize(8, 4)

sns.set()


# In[3]:


countries = pd.read_csv("countries.csv")


# In[12]:


new_column_names = [
    "Country", "Region", "Population", "Area", "Pop_density", "Coastline_ratio",
    "Net_migration", "Infant_mortality", "GDP", "Literacy", "Phones_per_1000",
    "Arable", "Crops", "Other", "Climate", "Birthrate", "Deathrate", "Agriculture",
    "Industry", "Service"
]

countries.columns = new_column_names
print(countries.head(5))


# ## Observações
# 
# Esse _data set_ ainda precisa de alguns ajustes iniciais. Primeiro, note que as variáveis numéricas estão usando vírgula como separador decimal e estão codificadas como strings. Corrija isso antes de continuar: transforme essas variáveis em numéricas adequadamente.
# 
# Além disso, as variáveis `Country` e `Region` possuem espaços a mais no começo e no final da string. Você pode utilizar o método `str.strip()` para remover esses espaços.

# ## Inicia sua análise a partir daqui

# In[ ]:


col_str = ['Country', 'Region']
col_int = ['Population', 'Area']


df_str = countries[col_str]
countries.drop(columns= col_str, inplace=True)

df_int = countries[col_int]
countries.drop(columns= col_int, inplace=True)

df_float = countries
col_flt = countries.columns


# In[ ]:


# conversion Int64
df_int = df_int.astype(int)


# In[ ]:


# convertion float

for col in df_float.columns:
    if col != 'GDP':
        df_float[col] = df_float[col].str.replace(',', '.')

df_float = df_float.astype(float)


# In[ ]:


# clean str
for col in df_str.columns:
    df_str[col] = df_str[col].str.strip()


# In[ ]:


countries = pd.concat([df_str, df_int, df_float], axis=1)


# ## Questão 1
# 
# Quais são as regiões (variável `Region`) presentes no _data set_? Retorne uma lista com as regiões únicas do _data set_ com os espaços à frente e atrás da string removidos (mas mantenha pontuação: ponto, hífen etc) e ordenadas em ordem alfabética.

# In[9]:


def q1():
    # Retorne aqui o resultado da questão 1.
    return np.sort(countries.Region.unique()).tolist()
    pass


# In[10]:


q1()


# ## Questão 2
# 
# Discretizando a variável `Pop_density` em 10 intervalos com `KBinsDiscretizer`, seguindo o encode `ordinal` e estratégia `quantile`, quantos países se encontram acima do 90º percentil? Responda como um único escalar inteiro.

# In[10]:


def q2():
    discretizer = KBinsDiscretizer(n_bins=10, encode="ordinal", strategy="quantile")
    score_bins = discretizer.fit_transform(countries[['Pop_density']])

    return int(sum(score_bins[:, 0] == 8))


# In[11]:


q2()


# # Questão 3
# 
# Se codificarmos as variáveis `Region` e `Climate` usando _one-hot encoding_, quantos novos atributos seriam criados? Responda como um único escalar.

# In[14]:


def q3():
    onehotencoder = OneHotEncoder(dtype='object')
    # imput data missing
    new_region = countries[['Region', 'Climate']].fillna(0)

    encoded = onehotencoder.fit_transform(new_region[['Region', 'Climate']])
    return encoded.shape[1]


# In[15]:


q3()


# ## Questão 4
# 
# Aplique o seguinte _pipeline_:
# 
# 1. Preencha as variáveis do tipo `int64` e `float64` com suas respectivas medianas.
# 2. Padronize essas variáveis.
# 
# Após aplicado o _pipeline_ descrito acima aos dados (somente nas variáveis dos tipos especificados), aplique o mesmo _pipeline_ (ou `ColumnTransformer`) ao dado abaixo. Qual o valor da variável `Arable` após o _pipeline_? Responda como um único float arredondado para três casas decimais.

# In[13]:


test_country = [
    'Test Country', 'NEAR EAST', -0.19032480757326514,
    -0.3232636124824411, -0.04421734470810142, -0.27528113360605316,
    0.13255850810281325, -0.8054845935643491, 1.0119784924248225,
    0.6189182532646624, 1.0074863283776458, 0.20239896852403538,
    -0.043678728558593366, -0.13929748680369286, 1.3163604645710438,
    -0.3699637766938669, -0.6149300604558857, -0.854369594993175,
    0.263445277972641, 0.5712416961268142
]


# In[18]:


def q4():
    pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy="median")),
        ('standardscaler', StandardScaler())               
    ])
    columns = np.concatenate((col_int, col_flt))

    pepiline_countries = pipeline.fit_transform(countries[columns])
    pepiline_test_countries = pipeline.transform([test_country[2:]])

    return float(pepiline_test_countries[0,9].round(3))
    pass


# In[19]:


q4()


# ## Questão 5
# 
# Descubra o número de _outliers_ da variável `Net_migration` segundo o método do _boxplot_, ou seja, usando a lógica:
# 
# $$x \notin [Q1 - 1.5 \times \text{IQR}, Q3 + 1.5 \times \text{IQR}] \Rightarrow x \text{ é outlier}$$
# 
# que se encontram no grupo inferior e no grupo superior.
# 
# Você deveria remover da análise as observações consideradas _outliers_ segundo esse método? Responda como uma tupla de três elementos `(outliers_abaixo, outliers_acima, removeria?)` ((int, int, bool)).

# In[12]:


def q5():
    q1_net_migration = countries.Net_migration.quantile(0.25)
    q3_net_migration = countries.Net_migration.quantile(0.75)

    iqr = q3_net_migration - q1_net_migration

    non_outlier_interval_iqr = [q1_net_migration - 1.5 * iqr, q3_net_migration + 1.5 *iqr]
    outlier_net_migration = [sum(countries.Net_migration < non_outlier_interval_iqr[0]),
                            sum(countries.Net_migration > non_outlier_interval_iqr[1])]

    outlier_net_migration.append(False)

    return tuple(outlier_net_migration)


# ## Questão 6
# Para as questões 6 e 7 utilize a biblioteca `fetch_20newsgroups` de datasets de test do `sklearn`
# 
# Considere carregar as seguintes categorias e o dataset `newsgroups`:
# 
# ```
# categories = ['sci.electronics', 'comp.graphics', 'rec.motorcycles']
# newsgroup = fetch_20newsgroups(subset="train", categories=categories, shuffle=True, random_state=42)
# ```
# 
# 
# Aplique `CountVectorizer` ao _data set_ `newsgroups` e descubra o número de vezes que a palavra _phone_ aparece no corpus. Responda como um único escalar.

# In[33]:


def load_newsgroup():
    categories = ['sci.electronics', 'comp.graphics', 'rec.motorcycles']
    return fetch_20newsgroups(subset="train", categories=categories, shuffle=True, random_state=42)


# In[34]:


def q6():
    word = 'phone'

    count_vectorizer = CountVectorizer()
    newgroups_counts = count_vectorizer.fit_transform(load_newsgroup().data)

    return int(newgroups_counts[ :, count_vectorizer.vocabulary_.get(word)].sum())
    pass


# In[35]:


q6()


# ## Questão 7
# 
# Aplique `TfidfVectorizer` ao _data set_ `newsgroups` e descubra o TF-IDF da palavra _phone_. Responda como um único escalar arredondado para três casas decimais.

# In[36]:


def q7():
    # Retorne aqui o resultado da questão 7.
    word = 'phone'

    tfidf_vectorizer = TfidfVectorizer()
    newsgroups_tfidf_vectorizer = tfidf_vectorizer.fit_transform(load_newsgroup().data)

    return float (newsgroups_tfidf_vectorizer[ :, tfidf_vectorizer.vocabulary_.get(word)].sum().round(3))
    pass


# In[37]:


q7()

