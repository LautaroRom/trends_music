import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import csv

def get_saturdays(start_date, end_date):
    current_date = start_date
    while current_date.weekday() != 5:  # 5 representa el sábado
        current_date += timedelta(days=1)
    
    saturdays = []
    while current_date <= end_date:
        saturdays.append(current_date)
        current_date += timedelta(weeks=1)
    
    return saturdays

def scrape_billboard_data(url, date, retries=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Esto generará un error para códigos de estado HTTP 4xx/5xx
            soup = BeautifulSoup(response.content, 'html.parser')
            chart_data = []

            # Seleccionar todas las filas del chart
            rows = soup.select('div.o-chart-results-list-row-container')

            for row in rows:
                position = row.select_one('li.o-chart-results-list__item span.c-label').get_text(strip=True)
                song = row.select_one('h3.c-title').get_text(strip=True)
                artist = row.select_one('span.c-label.a-no-trucate').get_text(strip=True)

                # Las siguientes selecciones pueden fallar si el elemento no existe
                last_week = row.select_one('li.o-chart-results-list__item:nth-of-type(3) span.c-label')
                peak_pos = row.select_one('li.o-chart-results-list__item:nth-of-type(5) span.c-label')
                weeks_on_chart = row.select_one('li.o-chart-results-list__item:nth-of-type(6) span.c-label')

                last_week = last_week.get_text(strip=True) if last_week else "N/A"
                peak_pos = peak_pos.get_text(strip=True) if peak_pos else "N/A"
                weeks_on_chart = weeks_on_chart.get_text(strip=True) if weeks_on_chart else "N/A"

                chart_data.append({
                    'Date': date,
                    'Position': position,
                    'Song': song,
                    'Artist': artist,
                    'Last Week': last_week,
                    'Peak Pos': peak_pos,
                    'Weeks on Chart': weeks_on_chart
                })
            return chart_data
        
        except requests.exceptions.RequestException as e:
            print(f"Error al acceder a {url}: {e}")
            if i < retries - 1:  # Si no es el último intento
                print("Reintentando...")
                time.sleep(2)  # Espera 2 segundos antes de reintentar
            else:
                return []

# Define el rango de fechas
start_date = datetime(1980, 1, 5)
end_date = datetime(2024, 6, 8)  # El último sábado antes de hoy

saturdays = get_saturdays(start_date, end_date)

start_time = time.time()  # Captura la hora de inicio

all_data = []
for saturday in saturdays:
    url = f"https://www.billboard.com/charts/hot-100/{saturday.strftime('%Y-%m-%d')}/"
    weekly_data = scrape_billboard_data(url, saturday.strftime('%Y-%m-%d'))
    all_data.extend(weekly_data)
    time.sleep(1)  # Espera 1 segundo entre solicitudes para evitar sobrecargar el servidor
    
end_time = time.time()  # Captura la hora de finalización

elapsed_time = end_time - start_time  # Calcula el tiempo transcurrido
    
# Exporta los datos a un archivo CSV
with open('billboard_hot_100_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['Date', 'Position', 'Song', 'Artist', 'Last Week', 'Peak Pos', 'Weeks on Chart'])
    writer.writeheader()
    writer.writerows(all_data)
    
# Imprime el tiempo total de ejecución
print(f"Tiempo total de ejecución: {elapsed_time:.2f} segundos")