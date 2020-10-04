from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser 
from rest_framework import status
import nltk
import os
from QM import Question_Manager
import googleapiclient.discovery
import json
from embedding import load_embedding
import logging
from django.conf import settings
fmt = getattr(settings, 'LOG_FORMAT', None)
lvl = getattr(settings, 'LOG_LEVEL', logging.DEBUG)

logging.basicConfig(format=fmt, level=lvl)
logging.debug("Logging started on %s for %s" % (logging.root.name, logging.getLevelName(lvl)))

# nltk.download('punkt')
# nltk.download('stopwords')

API_KEY = 'AIzaSyB-OHHc_t1PlT2TbiQY67-yUuAe7tqotfg'

ruta = os.path.join(os.path.abspath("."),"Consultas\\Embeddings")
ruta = os.path.join(ruta,"esTech_enTech_1.vec")
# EMBEDDING_PATH = '.\Embeddings\esTech_enTech_1.vec'
EMBEDDING_PATH = ruta

embedding = load_embedding(EMBEDDING_PATH)
QM2 = Question_Manager(embedding)

K_CLUSTERS = 3

MAX_COMMENTS = 50


def transformarListaComentarios_Json(ListaDeListas):
    ListaFinal=[]
    TemasNumeros=list(range(1,len(ListaDeListas)+1))
    for indice,Lista in enumerate(ListaDeListas):
        Dicc = {}
        data=[]
        Dicc["topic name"]="Tema #"+str(TemasNumeros[indice])
        for i,element in enumerate(Lista):
            DiccInterno = {}
            DiccInterno["name"]=element
            DiccInterno["value"]=len(Lista)-i
            data.append(DiccInterno)
        Dicc["data"]=data
        ListaFinal.append(Dicc)

    return ListaFinal

def transformarListaPalabras_Json(ListaDeTuplas):
    ListaFinal = []
    for Tupla in ListaDeTuplas:
        Dicc = {}
        Dicc["text"]=Tupla[0]
        Dicc["weight"]=Tupla[1]
        ListaFinal.append(Dicc)

    return ListaFinal

def getMessagesStreaming(LIVE_CHAT_ID):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = API_KEY

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.liveChatMessages().list(
        liveChatId=LIVE_CHAT_ID,
        part="snippet",        
        maxResults=85
    )
    response = request.execute()
    
    return response

def anadir_pregunta(itemsL):
    for item in itemsL:
        comentario = item["snippet"]["displayMessage"]
        QM2.add_question(comentario)

def director(LIVE_CHAT_ID):
    messageD = getMessagesStreaming(LIVE_CHAT_ID)
    itemsL = messageD["items"]
    anadir_pregunta(itemsL)
    kmeans = QM2.clustering(n_clusters=K_CLUSTERS)
    clusters = QM2.get_groups(kmeans)
    bubbles = transformarListaComentarios_Json(clusters)
    keywordL = QM2.get_keywords()
    wc = transformarListaPalabras_Json(keywordL)
    response = {"bubble":bubbles,"wc":wc}
    return response

@csrf_exempt
def consultas_list(request):
    if request.method == 'POST':
        objeto_data = JSONParser().parse(request)
        LIVE_CHAT_ID = objeto_data["liveChatId"]
        print("LIVE_CHAT_ID:%s" % LIVE_CHAT_ID)
        response = director(LIVE_CHAT_ID)
        return JsonResponse(response, safe=False)
