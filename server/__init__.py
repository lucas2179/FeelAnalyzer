from cloudant import Cloudant
from flask import Flask, render_template, request, jsonify, url_for, redirect, abort, session
import atexit
import os
import json
from TwitterSearch import *
import tweepy
from watson_developer_cloud import NaturalLanguageUnderstandingV1, LanguageTranslatorV3
from watson_developer_cloud.natural_language_understanding_v1 import Features, CategoriesOptions, EmotionOptions, SentimentOptions
from flask.json import jsonify

#Autenticando a API  do twitter
consumer_key = 'qXjupbOHLaOhWQqCKCe0MgVH9'
consumer_secret = 'YuuKuyag2YrZCNurcuj9TSXsbPLk0fU2713AFGdg3Iaany3CGF'
access_token = '183420642-foD4dNpZzfzk57U0JFh1tRe1e6FwSCj9Fku3KwLU'
access_token_secret = '5YNe4fJpKLOA7q3L9bpvCBDgpxZHxhGamAkl77a24lbQR'
autenticacao = tweepy.OAuthHandler(consumer_key, consumer_secret)
autenticacao.set_access_token(access_token, access_token_secret)
twitter = tweepy.API(autenticacao)

#autenticando api Natural Language Understanding
natural_language_understanding = NaturalLanguageUnderstandingV1(
	version = '2018-03-16',
	iam_apikey='vh26rIKrZatKT5hyVkCXqXphRh_mGBpGAUEnlqDwbVwi',
	url='https://gateway.watsonplatform.net/natural-language-understanding/api'
)

#autenticando api Language Translator 
language_translator = LanguageTranslatorV3(
    version='2018-05-01',
    iam_apikey='C_Q1nrk8L0QWalucVgn9mrMMHCx1HK8a73s2_aVycVW9',
    url='https://gateway.watsonplatform.net/language-translator/api'
)

#iniciando o Flask
app = Flask(__name__, template_folder="../public", static_folder="../public", static_url_path='')
if 'FLASK_LIVE_RELOAD' in os.environ and os.environ['FLASK_LIVE_RELOAD'] == 'true':
	import livereload
	app.debug = True
	server = livereload.Server(app.wsgi_app)
	server.serve(port=os.environ['port'], host=os.environ['host'])
# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))
resu =''
nome = ''
@app.route('/')
def root():
    return render_template("index.html")


#lendo o valor digitado pelo usuário na index.
@app.route("/verifica", methods=['GET', 'POST'])
def verifica():
	if request.method == "POST":
		global nome
		nome = request.form.get("nome")
		if nome:
			global resu
			resu = twitter.search(q=nome, l='en', src='typd') #querry para realizar a pesquisa.
	return redirect(url_for("resultado"))

#gerando os resultados
@app.route('/resultado')
def resultado():
	#iniciando variáveis da função
	soma2 = [0, 0, 0, 0, 0]
	cont = 0
	mediaemot=[0,0,0,0,0, '', 0, 0]
	con = 0
	soma = 0
	global resu
	global nome
	
	#lendo os tweets
	for tweet in resu:
		twi = json.dumps(tweet.text)
		r = ''

		try:
			#Nesta parte, a API natural Language Understanding é utilizada para fazer a analise de sentimento e reconhecer o idioma do tweet
			response = natural_language_understanding.analyze(
				text=twi,
				features=Features(sentiment=SentimentOptions(targets=[nome]))).get_result()
			print(json.dumps(response, indent=2))
			
			#como as emoções só são analisadas em inglês, caso o tweet esteja em outro idioma é necessário traduzi - lo para inglês
			if(response['language'] != "en"):
				try:
					translation = language_translator.translate(
    					text=twi,
    					model_id=response['language']+'-en').get_result()
					print(json.dumps(translation, indent=2, ensure_ascii=False))
					twi = translation['translations']
					twi2 = twi[0]
					twi3 = twi2['translation']
					twi4 = json.dumps(twi3)
					prossiga = True
				except:
					prossiga = False
			else:
				prossiga = True
				twi4 = twi
			if(prossiga == True):
				#com o tweet traduzido, as emoções contidas no mesmo são analisadas
				response2 = natural_language_understanding.analyze(
					text=twi4,
					features=Features(emotion=EmotionOptions(targets=[nome]))).get_result()
				print(json.dumps(response2, indent=2))
				cont = cont + 1
				print(cont)
				respon2 = json.dumps(response2, indent=2)
				respond2 = json.loads(respon2)
				responde2 = respond2['emotion']
				print(responde2)
				respondee3 = responde2['targets']
				print(respondee3)
				respondee2 = respondee3[0]
				respondeee = respondee2['emotion']
				print(json.dumps(respondee2))
				#OBS: esta troca de variáveis foi para selecionar as emoções dentro da estrutura que é retornada
				respondido2 = [respondeee['fear'], respondeee['disgust'], respondeee['sadness'], respondeee['anger'], respondeee['joy']]
				print(respondido2)
				for i in range(0,5):
					soma2[i] = soma2[i] + respondido2[i]
			else:
				print("no")

			respon = json.dumps(response,indent=2)
			respond = json.loads(respon)
			sentimento = respond['sentiment']
			sentimento2 = sentimento['targets']
			sent = sentimento2[0]
			senti = sent['label']
			sentscor = sent['score']
			soma = soma + sentscor
			con = con + 1
		except:
			print(" ")

	for i in range(0, 5):
		mediaemot[i] = soma2[i]/cont #fazendo a média de cada emoção
	print(mediaemot[0], mediaemot[1], mediaemot[2], mediaemot[3], mediaemot[4])
	mediaemot[6] = soma/con #fazendo a média dos sentimentos
	if(mediaemot[6] > 0):
		mediaemot[5] = "positive"
	elif(mediaemot[6] < 0):
		mediaemot[5] = "negative"
	else:
		mediaemot[5] = "neutro"
	mediaemot[7] = con
	return render_template("resultado.html",re=mediaemot)#nesse caso, mediaemot retorna a média das 5 emoções, a média do sentimento, o positive/negative e a quantidade de tweets analisados


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True) #inicia o aplicativo

