from QM import Question_Manager
from embedding import load_embedding
import os
ruta = os.path.join(os.path.abspath("."),"Consultas\\Embeddings")
ruta = os.path.join(ruta,"esTech_enTech_1.vec")
# EMBEDDING_PATH = '.\Embeddings\esTech_enTech_1.vec'
EMBEDDING_PATH = ruta
MAX_WORDS = 25

embedding = load_embedding(EMBEDDING_PATH)
QM2 = Question_Manager(embedding)


def anadir_pregunta(itemsL):
    for item in itemsL:
        comentario = item["snippet"]["displayMessage"]
        print(comentario)
        QM2.add_question(comentario)  
        print(QM2.questions_normalized)
        print(QM2.questions_vectors)

anadir_pregunta(["Esto es una prueba GGGG"])
