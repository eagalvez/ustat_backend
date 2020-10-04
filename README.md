# USTAT BACKEND #

### What is uStats? ###
uStats is a web tool that will allow you to monitor everything that happens with your YouTube live broadcast, from something as simple as general broadcast statistics, like number of likes, viewers,etc; till identify the topics and the frequently asked questions that arise in the chat.
### Why use uStats? ###
Thanks to uStats the streamer can increase their efficiency and effectiveness in reading and answering questions by covering as many topics as possible, not wasting time on repeated questions.

## Run the sever ## 
The backend of uStats project was created with django. In order to run the server please follow the next steps:


* Install the requirements for the project 
```
pip install -r requirements.txt
```
* Add an Embeddings folder on consultas with the embedding of this repository
*https://github.com/dccuchile/spanish-word-embeddings*
```
consultas\Embeddings\esTech_enTech_1.vec
```
* Run the the server
```
python manage.py runserver
```
* Realize a post method with the following body to the endpoint *http://localhost:8000/consultas/*
```
{
    "liveChatId":<live chat id of your live streaming>
}    
```
* You will be returned a json with the following structure

```
{
    "bubbles":...
    "wc":...
}
```

* Please check the front end on this respository *https://github.com/enmanuel-mag/ustats-v2*