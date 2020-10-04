import Dependencias.tensorflow_functions_2
# tensorflow_functions = importlib.reload(tensorflow_functions)
cosine_knn = Dependencias.tensorflow_functions_2.cosine_knn
import collections
import numpy as np
import logging
import operator
from sklearn.cluster import KMeans
from Dependencias.utilsf import length_normalize, normalize_questions, normalize_vector, calculate_cosine_simil, perf_measure
import sklearn.metrics
import argparse
import os
import datetime
MAX_WORDS = 25

class Question_Manager():
    questions = []
    questions_normalized = []
    questions_vectors = []
    keywords = collections.defaultdict()
    embedding = None

    def __init__(self, embedding_path='/home/iker/Documents/QuestionCluster/TechEmbeddings/embeddings_lower.vec'):
        self.questions = []
        self.questions_normalized = []
        self.questions_vectors = []
        self.keywords = collections.defaultdict()
        #self.embedding = load_embedding(embedding_path)
        self.embedding = embedding_path
    
    def pad_sentence(self, sentence,dims):
        try:
            if len(sentence) >= MAX_WORDS:
                return sentence[:MAX_WORDS]
            else:
                while(len(sentence) < MAX_WORDS):
                    sentence = np.concatenate((sentence,[np.zeros(dims)]),axis=0)            
                return sentence
        except:
            print('Error in sentence: ' + str(sentence))
            raise ValueError('ReadingError')

    def get_keywords(self):#lista de las palabras mas repetidas ordenadas
        return sorted(self.keywords.items(), key=operator.itemgetter(1), reverse=True)

    def question_to_vector(self, question, prefix=False):
        sentence = np.zeros([self.embedding.dims])
        num_words = 0
        
        
        
        for word in question:
            try:
                if prefix:
                    sentence += self.embedding.word_to_vector(prefix+'/'+word)
                else:
                    sentence += self.embedding.word_to_vector(word)
                num_words += 1
            except KeyError as r:
                continue

        if num_words > 0:
            sentence = sentence / num_words
        else:
            logging.warning(
                'Could not calculate the sentence embedding fot the sentence ' + str(question))

        return sentence    
        #return self.pad_sentence(sentence, embedding.dims)

    def update_keyword_for_sentence(self, question):
        for word in question:
            try:
                self.keywords[word] += 1
            except KeyError as er:
                self.keywords[word] = 1

    def print_question(self, question, path='questions.txt'):
        with open(path, 'a', encoding='utf-8') as file:
            print(str(question), file=file)

    def add_question(self, question):
        normalized_question = normalize_questions(question)
        question_vector = self.question_to_vector(normalized_question)
        if len(normalized_question) > 0 and question_vector is not None:
            self.questions.append(question)
            self.questions_normalized.append(normalized_question)
            self.questions_vectors.append(question_vector)
            self.update_keyword_for_sentence(normalized_question)
            self.print_question(question)

    def load_form_file(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            for no, line in enumerate(file):
                self.add_question(line)
            print(f'Numero de preguntas {no}')
            
    def clustering(self, n_clusters=8):
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(
            np.array(self.questions_vectors))
        
        labels = kmeans.labels_

        questions_cluster = [[] for x in range(n_clusters)]
        return kmeans
        #for i_label, label in enumerate(labels):
        #    questions_cluster[label].append(self.questions[i_label])
        
        #for i_label, label in enumerate(kmeans.predict(np.array(self.questions_vectors))):
        #    questions_cluster[label].append(self.questions[i_label])

        #return questions_cluster
    
    def get_groups(self, kmeans_i):
        labels = kmeans_i.labels_
        
        questions_cluster = [[] for x in range(len(kmeans_i.cluster_centers_))]
        
        for i_label, label in enumerate(labels):
            questions_cluster[label].append(self.questions[i_label])
            
        return questions_cluster
        

    def k_nearest(self, sentence, k=1):
        vectors_norm = length_normalize(np.array(self.questions_vectors))
        result = cosine_knn([self.question_to_vector(
            normalize_questions(sentence))], vectors_norm, k=k)

        for s in result[0]:
            print(self.questions[s])

    def evaluate_similarity(self, question_file, threshold=0.8, prefix=False):
        question1 = []
        question2 = []
        gold_scores = []

        with open(question_file) as file:
            for line in file:
                line = line.rstrip()
                q1, q2, gold = line.split('\t')
                question1.append(q1)
                question2.append(q2)
                gold_scores.append(int(gold))

        question_vectors_1 = [self.question_to_vector(
            normalize_questions(x), prefix) for x in question1]
        question_vectors_2 = [self.question_to_vector(
            normalize_questions(x), prefix) for x in question2]

        scores = []
        for i in range(len(question_vectors_1)):
            if i % 10 == 0:
                string = "<" + str(datetime.datetime.now()) + ">  " + 'Evaluating Question Pairs: ' + str(
                    int(100 * ((i+10) / len(question_vectors_1)))) + '%'
                print(string, end="\r")

            score = calculate_cosine_simil(
                question_vectors_1[i], question_vectors_2[i])
            if score > threshold:
                scores.append(1)
            else:
                scores.append(0)
        print()
        result = sklearn.metrics.log_loss(gold_scores, scores)
        TP, FP, TN, FN = perf_measure(gold_scores, scores)
        acc = np.sum(np.array(gold_scores) ==
                     np.array(scores))/len(gold_scores)

        print('Log Loss: ' + str(result))
        print('Acc: ' + str(acc))
        print('TP: ' + str(TP) + '\tFP: ' + str(FP) +
              '\tTN: ' + str(TN) + '\tFN: ' + str(FN))
        print(scores)
        print(gold_scores)
        return result, acc, TP, FP, TN, FN