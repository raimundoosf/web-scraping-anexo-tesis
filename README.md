# Web Scraper SNIFA: Análisis de Concentración de Unidades Fiscalizables

Este repositorio/directorio contiene el código fuente y la metodología utilizada para extraer y analizar la titularidad de las Unidades Fiscalizables (UFs) reguladas por la Superintendencia del Medio Ambiente (SMA) de Chile. El objetivo principal es cuantificar la concentración de proyectos ambientales por empresa (RUT) a nivel nacional.

## 📌 Contexto del Problema
El portal de Datos Abiertos del [Sistema Nacional de Información de Fiscalización Ambiental (SNIFA)](https://snifa.sma.gob.cl/DatosAbiertos) provee un catastro público de instalaciones (UFs). Sin embargo, la base de datos descargable omite la variable del **RUT del Titular**, entregando únicamente un hipervínculo a la ficha pública de cada proyecto. 

Este proyecto soluciona esa limitación técnica mediante un *web scraper* automatizado que visita cada ficha, extrae el RUT de la entidad legal correspondiente y consolida una base de datos apta para el análisis estadístico.

## ⚙️ Requisitos Previos
El script fue desarrollado para ejecutarse en entornos Linux/Windows/macOS utilizando **Python 3**. Las dependencias necesarias son:

* `pandas` (Manejo y análisis de bases de datos)
* `requests` (Peticiones HTTP)
* `beautifulsoup4` (Parsing de HTML)

**Instalación (Recomendado usar un entorno virtual):**
```bash
python -m venv venv
source venv/bin/activate  # En Windows usar: venv\Scripts\activate
pip install pandas requests beautifulsoup4
