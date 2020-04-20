# FBScraper
Facebook scraper obtiene la siguiente información las publicaciones de los perfiles indicados, publicadas en el rango de fecha establecido:
  - Veces compartida
  - Comentarios
  - Reacciones ('Me gusta','Me encanta','Me asombra','Me entristece','Me enoja','Me divierte')

Los resultados son guardados en un archivos xlsx en la carpeta donde se ejecutó el script con el formato perfilYYMMdd.xlsx 

## Pre-requisitos
- El perfil de Facebook debe estar en español
- Chromedriver (https://chromedriver.chromium.org/downloads)
#### Paquetes Pyhton
 -selenium
 -BeautifulSoup
 -pandas
 
 ## Uso
 Modificar en lineas 277 a 281:
  - Fecha de inicio y fecha final
  - Usuario y contraseña
  - Perfiles a scrapear
 
 
