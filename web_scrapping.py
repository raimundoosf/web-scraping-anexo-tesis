import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os

# 1. Cargar datos originales
df = pd.read_csv("UF_Instrumentos.csv", sep=";", on_bad_lines='skip', encoding='latin1')
df['LinkSNIFA'] = df['LinkSNIFA'].astype(str).str.strip()
links_unicos = df['LinkSNIFA'].unique()

# Archivo donde guardaremos el progreso real
ARCHIVO_PROGRESO = "progreso_scraping.csv"

# Revisar si ya existía progreso previo para no empezar desde cero si se corta el internet
if os.path.exists(ARCHIVO_PROGRESO):
    df_progreso_previo = pd.read_csv(ARCHIVO_PROGRESO, encoding='utf-8')
    links_procesados = set(df_progreso_previo['LinkSNIFA'].tolist())
    titulares = df_progreso_previo.to_dict(orient="records")
    print(f"🔄 Resumiendo progreso anterior. Ya se habían procesado {len(links_procesados)} enlaces.")
else:
    links_procesados = set()
    titulares = []
    print("🆕 Iniciando un nuevo proceso de extracción.")

print(f"Total de enlaces únicos a procesar: {len(links_unicos)}")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 2. Extraer datos (SIN LÍMITE DE 10)
contador = len(links_procesados)

for link in links_unicos: 
    if not link.startswith("http"): continue
    if link in links_procesados: continue # Saltarse los que ya se hicieron antes
        
    try:
        res = requests.get(link, headers=headers, timeout=10)
        contador += 1
        
        if res.status_code != 200:
            print(f"[{contador}/{len(links_unicos)}] [BLOQUEADO/ERROR] Código {res.status_code} en {link}")
            continue
            
        soup = BeautifulSoup(res.text, 'html.parser')
        etiqueta_rut = soup.find(lambda tag: tag.name in ["th", "td", "label"] and "RUT" in tag.text.upper())
        
        if etiqueta_rut:
            nodo_valor = etiqueta_rut.find_next("td")
            if nodo_valor:
                rut = nodo_valor.text.strip()
                # Guardar registro
                nuevo_registro = {'LinkSNIFA': link, 'RUT': rut}
                titulares.append(nuevo_registro)
                links_procesados.add(link)
                print(f"[{contador}/{len(links_unicos)}] [ÉXITO] RUT: {rut}")
                
                # Guardar inmediatamente en el disco duro (por seguridad)
                pd.DataFrame([nuevo_registro]).to_csv(ARCHIVO_PROGRESO, mode='a', header=not os.path.exists(ARCHIVO_PROGRESO), index=False, encoding='utf-8')
            else:
                links_procesados.add(link)
        else:
            # Es un particular o no tiene RUT expuesto, guardamos como "No Registra" para no volver a consultarlo
            nuevo_registro = {'LinkSNIFA': link, 'RUT': 'NO_REGISTRA'}
            titulares.append(nuevo_registro)
            links_procesados.add(link)
            pd.DataFrame([nuevo_registro]).to_csv(ARCHIVO_PROGRESO, mode='a', header=not os.path.exists(ARCHIVO_PROGRESO), index=False, encoding='utf-8')
            print(f"[{contador}/{len(links_unicos)}] [PASADO] Particular o sin RUT en: {link}")
            
        time.sleep(1) # IMPORTANTE: Mantiene la tasa de peticiones segura
        
    except Exception as e:
        print(f"Error inesperado en {link}: {e}")
        time.sleep(5) # Si hay un error de red, espera 5 segundos antes de reintentar

# 3. Análisis Final cuando termine el 100%
print("\n--- PROCESAMIENTO Y ANÁLISIS DE DATOS ---")
if os.path.exists(ARCHIVO_PROGRESO):
    df_final = pd.read_csv(ARCHIVO_PROGRESO, encoding='utf-8')
    # Limpiar registros que no pertenecen a empresas (personas naturales)
    df_final = df_final[df_final['RUT'] != 'NO_REGISTRA']

    # Contar cuántas UFs tiene cada RUT único
    conteo = df_final.groupby("RUT").size()

    # Calcular los 4 umbrales solicitados de forma instantánea
    empresas_mas_5  = conteo[conteo > 5]
    empresas_mas_10 = conteo[conteo > 10]
    empresas_mas_15 = conteo[conteo > 15]
    empresas_mas_20 = conteo[conteo > 20]

    # Mostrar los resultados resumidos en pantalla
    print(f"Resultados basados en {df_final['LinkSNIFA'].nunique()} instalaciones analizadas:")
    print(f"🔹 Empresas con más de  5 UFs: {len(empresas_mas_5)}")
    print(f"🔹 Empresas con más de 10 UFs: {len(empresas_mas_10)}")
    print(f"🔹 Empresas con más de 15 UFs: {len(empresas_mas_15)}")
    print(f"🔹 Empresas con más de 20 UFs: {len(empresas_mas_20)}")
    
    print(f"\nLos resultados detallados por enlace siguen respaldados en: '{ARCHIVO_PROGRESO}'")
else:
    print("No se encontró el archivo de progreso para analizar.")