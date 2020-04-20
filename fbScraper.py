# -*- coding: utf-8 -*-
"""
@author: iquelo@gmail.com
"""

from datetime import date
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import time
from bs4 import BeautifulSoup
import pandas as pd
import locale
import json
import sys

class fbScraper:
    
    def __init__(self,perfiles,usuario,password,fecha_inicio,fecha_fin,corte):
        self.corte=corte
        self.start = time.time()
        self.__perfiles=perfiles
        self.fecha_inicio=fecha_inicio
        self.fecha_fin=fecha_fin
        self.corte=corte
        chrome_options = Options()  
        chrome_options.add_argument("--headless") 
        print ('Iniciando navegador')
        self.driver = webdriver.Chrome('chromedriver.exe',options=chrome_options) 
        self.login(usuario,password)
        
        for perfil in perfiles:
            locale.setlocale(locale.LC_ALL, 'es_ES')
            url='https://mobile.facebook.com/'+ perfil + '/posts/'
            print('-----------------------------------------')
            print('Comenzando a scrapear ' + perfil)  
            self.driver.get(url)
            self.scrollDown(1,1)
            
            self.scrollDownFecha(0)
            perf=self.driver.page_source
            soup = BeautifulSoup(perf, 'html.parser')
            stories=soup.findAll("div", {"class": "_3drp"})
            cont=1
            publis=[]
            storiesV=[]
            
            for story in stories:
                fecha=self.traeFecha(story)
                #print(fecha)
                if fecha >= self.fecha_inicio and fecha <= self.fecha_fin:
                    st={'story':story,'fecha':fecha}
                    storiesV.append(st)
            print('\nSe encontraron ' + str(len(storiesV)) + ' publicaciones entre las fechas ' + str(fecha_inicio) + ' y ' + str(fecha_fin))
            
            
            for st in storiesV:
                lineaScrap='Scrapeando publicación ' + str(cont) + ' de ' +  str(len(storiesV))
                sys.stdout.write('\r'+lineaScrap)
                publis.append(self.scrapStory(st['story'],st['fecha']))
                cont+=1
            
            locale.setlocale(locale.LC_ALL, 'us_US')
            self.pdf=pd.DataFrame(publis)
            fecha = date.today().strftime("%Y%m%d")
            archivo= perfil + '_' + fecha
            self.pdf.to_excel(archivo + '.xlsx')
            end = time.time()
            totalTime=int(end - self.start)
            print ('\nTiempo transcurrido: ' + str(totalTime) + ' segundos')
            
    def muestra_Datos(self):
        if self.pdf:
            return self.pdf
        else:
            print ('No se encontraron los datos')
            
    def traeFecha(self,story):
        dt=story.findAll("div", {"class": "_52jc _5qc4 _78cz _24u0 _36xo"})
        f=dt[0].get_text()
        if ' h ·' not in f and 'min ·' not in f and 'Ayer' not in f:
            n=f.split(' de ')
            try:
                int(n[0])
                diaP=1
            except:
                diaP=0
            if diaP==1:
                dia=n[0]
                if len(n)==2:
                    mes=n[1].split(' ')[0]
                    ano='2020'
                else:
                    mes=n[1]
                    ano=n[2].split(' ')[0]
            else:
                dia='01'
                mes=n[0]
                ano=n[1].split(' ')[0]
            fecha=datetime.strptime(dia + '-' + str(mes) + '-' + ano, '%d-%B-%Y')
        else:
            fecha=datetime.today()
        
        return fecha
    

    def scrollDownFecha(self,SCROLL_PAUSE_TIME):
        n=1
        print('Buscando publicaciones posteriores al ' + str(fecha_inicio))
        while True:
            last_h = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            new_h=self.driver.execute_script("return document.body.scrollHeight")
            while new_h== last_h:
                new_h= self.driver.execute_script("return document.body.scrollHeight")
            nScroll= 'Scroll nro: ' + str(n) 
            sys.stdout.write('\r'+nScroll)
            n+=1
            if n % self.corte==0:
                perf=self.driver.page_source
                soup = BeautifulSoup(perf, 'html.parser')
                stories=soup.findAll("div", {"class": "_3drp"})
                fecha=self.traeFecha(stories[len(stories)-1])
                lineaScroll= '\nScroll nro: ' + str(n) + ' contiene hasta ' + str(fecha)
                #sys.stdout.write('\n\r'+lineaScroll)
                print (lineaScroll)
                if fecha <= fecha_inicio:
                    break

        
    def scrollDown(self,SCROLL_PAUSE_TIME, SCROLL_LIMIT):
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        n=0
        while True:
            if (n==SCROLL_LIMIT):
                break
            n+=1
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
            time.sleep(SCROLL_PAUSE_TIME)
        
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def masDeMil(self,lnk):
        #print(lnk)
        
        lnk='https://mobile.facebook.com' + lnk.split('&')[0] + '&' + lnk.split('&')[1]
        self.driver.get(lnk)
        perf=self.driver.page_source
        soup = BeautifulSoup(perf, 'html.parser')
        a=soup.find("span", {"data-sigil": "feed-ufi-sharers"})
        text=a.get_text()
        comp=int(text.split(' ')[0].replace('.',''))
        return comp
    
    def masDeMiltxt(self,txt):
        r=txt.split('\xa0')[0].replace(',','.')
        r=int(float(r)*1000)
        return r
    
    
    def emparejaNom(self,nombre):
        if 'video' in nombre:
            return 'video'
        elif 'photo' in nombre or 'album' in nombre or 'profile_media' in nombre:
            return 'photo'
        elif 'share' in nombre:
            return 'link'
        elif 'event' == nombre:
            return 'event'
        elif 'note' == nombre:
            return 'status'
        else:
            return nombre
    
    def login(self,usuario,password):
        self.driver.get('https://mobile.facebook.com')
        self.driver.find_element_by_id('m_login_email').clear()
        self.driver.find_element_by_id('m_login_email').send_keys(usuario) #CAMBIAR MAS ARRIBA
        self.driver.find_element_by_id('m_login_password').send_keys(password) #CAMBIAR MAS ARRIBA
        self.driver.find_element_by_name('login').click()
        time.sleep(2)
        self.driver.find_element_by_class_name('_54k8._56bs._26vk._56b_._56bw._56bt').click()
    
    
    def close_driver(self):
        self.driver.quit()
    
    def status(self):
        print (self.__perfiles)

    def scrapStory(self,story,fechaV):
        a=story.findAll("span", {"class": "_1j-c"})
        article=story.findAll("article", {"class": "_55wo _5rgr _5gh8 _3drq async_like"})
        dft=article[0].attrs['data-ft']
        jsonD=json.loads(dft)
        url=''
        tipo='status'
        if 'content_owner_id_new' in jsonD and 'mf_story_key' in jsonD:
            owner=jsonD['content_owner_id_new']
            storyKey=jsonD['mf_story_key']
            url='https://www.facebook.com/story.php?story_fbid='+storyKey+'&id='+owner+'&__tn__=-R'
        if 'story_attachment_style' in jsonD:
            tipo=jsonD['story_attachment_style']
        else:
            if 'story_attachment_style' in jsonD:
                tipo=jsonD['story_attachment_style']
            else:
                if 'attached_story_attachment_style' in jsonD:
                    tipo=jsonD['attached_story_attachment_style']
                
    
        lnkM=story.find("div", {"class": "_52jc _5qc4 _78cz _24u0 _36xo"})
        lnkM=lnkM.findAll("a", href=True)
        
        lnk='https://www.facebook.com'+lnkM[0].attrs['href']
        
        storyURL='https://mobile.facebook.com/ufi/reaction/profile/browser/?ft_ent_identifier='+lnkM[0].attrs['href'].split('&')[0].split('=')[1]
        reacciones='Me gusta','Me encanta','Me asombra','Me entristece','Me enoja','Me divierte'
        
        props={}
        props['Comentarios']=0
        props['Compartido']=0
        for c in a:
            if ('comentario' in c.get_text()):
                try:
                    props['Comentarios']=int(c.get_text().split(' ')[0])
                except:
                    props['Comentarios']=int(self.masDeMiltxt(c.get_text().split(' ')[0]))
            else:
                try:
                    props['Compartido']=int(c.get_text().split(' ')[0])
                except:
                    props['Compartido']=int(self.masDeMiltxt(c.get_text().split(' ')[0]))
       
        props['tipo']=self.emparejaNom(tipo)
        props['Fecha']=fechaV.strftime('%d/%m/%Y')
        if url:
            props['link']=url
        else:
            props['link']=lnk
        txt=''
        rt=story.findAll("p")
        if (len(rt))>0:
            for pg in rt:
                txt+=pg.text 
            
        props['Texto']=txt
        #props['Texto']=txt
        for re in reacciones:
            props[re]=0
        self.driver.get(storyURL)
        perf=self.driver.page_source
        soup = BeautifulSoup(perf, 'html.parser')
        rTotal=0
        
           
        r=soup.findAll("span", {"class": "_5p-9 _5p-l"})
        for i in r:
            for re in reacciones:
                if (re in i["aria-label"]):
                    
                    try:
                        props[re]=int(i.text)
                        rTotal=rTotal + int(i.text)
                    except:
                        props[re]=self.masDeMiltxt(i.text)
                        rTotal=rTotal+props[re]
                    
        props['Total']= rTotal    
        return props    

fecha_inicio=datetime.strptime('08-04-2020', '%d-%m-%Y')
fecha_fin=datetime.strptime('13-04-2020', '%d-%m-%Y')
usuario='USUARIO' #CAMBIAR POR USUARIO
password='PASSWORD' #CAMBIAR POR CONTRASEÑA
perfiles=['perfil1','perfil2','perfil3']

scraper=fbScraper(perfiles,usuario,password,fecha_inicio,fecha_fin,5)       


