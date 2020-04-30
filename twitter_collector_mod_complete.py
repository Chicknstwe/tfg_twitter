# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 17:40:50 2020

@author: memer
"""

usernames = ['el_pais',
             'El_Pais',
             'A3Noticias',
             'eldiarioes',
             'LaVanguardia',
             'elEconomistaes'
             'la_SER',
             'SextaNoticias',
             'abc_es',
             'elconfidencial',
             'expansioncom',
             'rtve',
             'COPE',
             'elmundoes',
             'publico_es',
             'OndaCero_es',
             'Newtral',
             'elespanolcom',
             'Cuatro',
             'noticias_cuatro',
             'elperiodico',
             'ElPeriodico',
             'La2_TVE',
             'ctxt_es',
             'informativost5',
             '_infoLibre',
             'ElSaltoDiario',
             'rne',
             'EFEnoticias',
             'materia_ciencia',
             'ideal_granada',
             'DiarioSUR',
             'laSextaTV',
             'La1_tve',
             '24H_tve',
             '20m',
             'larazon_es',
             'antena3com',
             'elpaissemanal',
             'tve_tve']

hashtags = ['COVID19',
            'QuedateEnCasa',
            'coronavirus']


class TwitterCollector():
    
    def __init__(self):
        
        import json
        import twitter
        
        try:
            with open('oauth.json', 'r') as file:
                self.oauth = json.load(file)
                
        except:
            self.generateOauth()
            with open('oauth.json', 'r') as file:
                self.oauth = json.load(file)
        
        self.CONFIG = {'show_rate_limit':True,
                       'search_remaining':180,
                       'app_remaining':180}        
        
        self.api = twitter.Api(consumer_key=self.oauth['consumer_key'],
                  consumer_secret=self.oauth['consumer_secret'],
                  access_token_key=self.oauth['access_token_key'],
                  access_token_secret=self.oauth['access_token_secret'],
                  tweet_mode='extended',
                  sleep_on_rate_limit=True)        

        
    def generateOauth(self):
        
        import json
        
        tokens = {'consumer_key':None, 'consumer_secret':None, 'access_token_key':None, 'access_token_secret':None}
        
        print('No existe archivo de autoridad o está corrupto. Se creará uno nuevo.')
        
        for key in tokens.keys():
            token = input('Por favor, escriba su {}.'.format(key))
            tokens[key] = token.strip()
            
        with open('oauth.json', 'w+') as file:
            file.write(json.dumps(tokens))
        
        # This checks if everything went fine
        with open('oauth.json', 'r') as file:
            oauth = json.load(file)
        if oauth == tokens:
            print('El archivo se ha creado correctamente.')
                      
    def executeQueries(self, username='', hashtag=''):
        """
        Inicia el proceso de recolección de tweets usando la REST API de twitter para cada cuenta proporcionada por el usuario.
        
        Si el proceso se ejecuta exitosamente, los tweets son codificados y guardados en archivos JSON en el directorio database
        """
        import twutilsmod as twutils
        import json
        import time
        from datetime import datetime as t
        
        if self.CONFIG['search_remaining'] < 3 or self.CONFIG['app_remaining'] < 3:
            print('El límite de la API está a punto de alcanzarse, por lo que no se ha ejecutado ninguna búsqueda.\nEste límite se reinicia en 15 minutos, así que el código se puede ejecutar de nuevo transcurrido este tiempo.')
        else:
            if 'database' not in twutils.getFoldersInFolder():
                twutils.createFolder('./database/')
    
            now = t.now()
    
            file_name = '{} {} {}-{}-{} {}h {}m'.format(username, hashtag, now.day, now.month, now.year, now.hour, now.minute)
            
            with open('./database/{}.json'.format(file_name), 'w+') as file:
                file.write('{')
            
            counter = 0
            tweet_quantity = 0        
        
            while not twutils.connected():
                print('No se detecta conexión a internet. Volviendo a conectar en 15 segundos.')
                time.sleep(15)
            
            # Twitter statuses como dicts en lugar de objetos Status
            raw_statuses = [status.__dict__ for status in self.api.GetSearch(raw_query="q=from%3A{}%20%23{}-filter%3Aretweets&result_type=popular&lang=es&count=200".format(username, hashtag))]
            if len(raw_statuses) > 0:
                # Se filtran los resultados para obtener únicamente los campos de interés
                statuses = twutils.filterStatuses(raw_statuses)
                
                tweet_quantity += len(statuses)
                
                encoded_statuses = json.dumps(statuses, sort_keys=True)
        
                with open('./database/{}.json'.format(file_name), 'a+') as file:
                    file.write(encoded_statuses[1:-1])
    
            else:
                statuses = {}
                
            with open('./database/{}.json'.format(file_name), 'a+') as file:
                file.write('}')
                
            counter += 1
            
            print('Tweets recopilados para @{} y #{}: {}'.format(username, hashtag, tweet_quantity))

            search_limit = self.api.rate_limit.resources['search']['/search/tweets']['limit']
            search_remaining = self.api.rate_limit.resources['search']['/search/tweets']['remaining']
            app_limit = self.api.rate_limit.resources['application']['/application/rate_limit_status']['limit']
            app_remaining = self.api.rate_limit.resources['application']['/application/rate_limit_status']['remaining']
            
            self.CONFIG['search_remaining'] = search_remaining
            self.CONFIG['app_remaining'] = app_remaining
            
            if self.CONFIG['show_rate_limit']:
                print('Solicitudes restantes (search): {} / {}'.format(search_remaining, search_limit))
                print('Solicitudes restantes (rate limit status): {} / {}'.format(app_remaining, app_limit))
            
            
    def exportToUnitaryExcel(self):
        """
        Exporta a excel los archivos json del directorio folder_name usando el modo disponible en self.CONFIG['export_mode'].
        
        input: string folder_name
        """
        
        from openpyxl import Workbook
        from twutilsmod import getFilesInFolder
        import json
        
        folder_name = './database/'
        
        files = getFilesInFolder(folder_name)
        
        json_files = [file for file in files if file[-5:] == '.json']
        total_statuses_n = 0
        all_tweets = {}
        repeated_tw = 0
        repeated_tws = {}
        
        for file in json_files:
            
            with open(folder_name + file, 'r') as tw_file:
                statuses = json.load(tw_file)              
            
            total_statuses_n += len(statuses)
            
            # Interesa ver si hay alguno repetido, por eso se usa este bucle 
            # en lugar del método dict.update()
            for tw_id, content in statuses.items():
                
                if tw_id in all_tweets.keys():
                    repeated_tw += 1
                    repeated_tws[tw_id] = content
                    repeated_tws[tw_id]['id'] = tw_id
                else:
                    all_tweets[tw_id] = content
                    all_tweets[tw_id]['id'] = tw_id
        
        if len(all_tweets) > 0:
            wb = Workbook()
            ws = wb.active
            
            ws.append(list(all_tweets[list(all_tweets.keys())[0]].keys()))
            
            for status in all_tweets.values():
                ws.append(list(status.values()))
                
            wb.save('{}all_tweets.xlsx'.format(folder_name))
        
        if len(repeated_tws) > 0:
            wb = Workbook()
            ws = wb.active
            
            ws.append(list(repeated_tws[list(repeated_tws.keys())[0]].keys()))
            
            for status in repeated_tws.values():
                ws.append(list(status.values()))
                
            wb.save('{}repeated_tweets.xlsx'.format(folder_name))

        print('Se han convertido un total de {} tweets.'.format(total_statuses_n))
        print('De los tweets convertidos, {} estaban repetidos. Si este número es mayor que 0, se han exportado al archivo repeated_tweets.xlsx.'.format(len(repeated_tws)))
        print('En definitiva, se han exportado a excel {} tweets únicos al archivo all_tweets.xlsx.'.format(len(all_tweets)))


if len(usernames)*len(hashtags) >= 178:
    print('Hay demasiadas cuentas y/o hastags. Si se ejecutara el código, se alcanzaría el límite de la API.\nEl límite es de 180 solicitudes. Se realiza una búsqueda por cada cuenta para cada hashtag.\n Teniendo en cuenta lo anterior, el número de búsquedas es [número de cuentas] * [número de hashtags].')
else:
    a = TwitterCollector()
    
    for username in usernames:
        for hashtag in hashtags:
            if a.CONFIG['search_remaining'] > 2 and a.CONFIG['app_remaining'] > 2:
                a.executeQueries(username, hashtag)
            else:
                break
        if a.CONFIG['search_remaining'] < 3 and a.CONFIG['app_remaining'] < 3:
            print('El límite de la API está a punto de alcanzarse, por lo que no se ha ejecutado ninguna búsqueda.\nEste límite se reinicia en 15 minutos, así que el código se puede ejecutar de nuevo transcurrido este tiempo.')
            break
            
    a.exportToExcel()

