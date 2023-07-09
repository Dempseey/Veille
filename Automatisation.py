import requests
import json
import pickle
import os
import yt_dlp
import re
import time

API_KEY = ""
CHANNEL_ID = "UCbfYPyITQ-7l4upoX8nvctg"

# Requête pour récupérer les vidéos d'une chaîne
def get_videos_from_channel(CHANNEL_ID, api_key):
    url = f"https://www.googleapis.com/youtube/v3/search?order=date&part=snippet&channelId={CHANNEL_ID}&maxResults=50&key={api_key}"
    response = requests.get(url)
    json_data = json.loads(response.text)
    video_urls = []
    for item in json_data['items']:
        if item['id']['kind'] == "youtube#video":
            video_urls.append(f"https://www.youtube.com/watch?v={item['id']['videoId']}")
    return video_urls

def create_list_url(video_list):
    #Utilisation de la fonction pour récupérer les vidéos de la chaîne spécifiée
    with open('url_list.pkl', 'wb') as f:
        pickle.dump(video_list, f)

def has_subtitles(video_url):
    ydl_opts = {
        'listsubtitles': True,
        'skip_download': True,  # Ne pas télécharger la vidéo
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        subtitles = info_dict.get('subtitles', {})
        
        # Vérifier si des sous-titres sont disponibles pour la langue 'en'
        return 'en' in subtitles

def generate_subtitles(video_url):
    if has_subtitles(video_url):
            
        ydl_opts = {
            'writesubtitles': True,
            'subtitleslangs': ['en'],  # Langue des sous-titres (en pour anglais)
            'skip_download': True,  # Ne pas télécharger la vidéo
            'subtitlesformat': 'vtt',  # Format des sous-titres
            'outtmpl': os.path.join('Sous_Titres', '%(upload_date)s.%(ext)s'),  # Modèle de nommage du fichier de sortie
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            ydl.prepare_filename(info_dict)

            # Téléchargement des sous-titres
            ydl.download([video_url])

            # Récupérer la date de parution et la formater
            upload_date = info_dict['upload_date']

            # Chemin du fichier de sous-titres généré
            original_file_path = os.path.join('Sous_Titres', f"{upload_date}.en.vtt")

            # Lire le contenu du fichier de sous-titres
            with open(original_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Filtrer les lignes indésirables
            filtered_lines = []
            for line in lines:
                if not re.match(r'^\d{2}:\d{2}:\d{2}.\d{3} --> \d{2}:\d{2}:\d{2}.\d{3}$', line.strip()) and not line.startswith('WEBVTT') and not line.startswith('Kind') and not line.startswith('Language'):
                    filtered_lines.append(line)
            # Supprimer les balises HTML et les espaces spéciaux
            filtered_lines = [re.sub(r'<[^>]+>', '', line) for line in filtered_lines]
            filtered_lines = [line.replace('&nbsp;', ' ') for line in filtered_lines]
            filtered_lines = [' '.join(line.strip() for line in filtered_lines if line.strip())]
            
            # Chemin du fichier nettoyé avec le titre de la vidéo
            cleaned_file_path = os.path.join('Sous_Titres', f"{upload_date}.srt")

            # Écrire le contenu nettoyé dans le fichier
            with open(cleaned_file_path, 'w', encoding='utf-8') as file:
                file.writelines(filtered_lines)
            
            # Supprimer le fichier non nettoyé
            os.remove(original_file_path)

def create_file_subtitle(url_list):
    for url in url_list:
        generate_subtitles(url)
        time.sleep(0.2)


def main():
    video_list = get_videos_from_channel(CHANNEL_ID, API_KEY)
    #Vérifier si le fichier existe déjà ou non 
    fichier = "url_list.pkl"
    if os.path.exists(fichier):
        print("Le fichier existe.")
    else:
        create_list_url(video_list)
    
    #Création des fichiers de sous-titres
    with open(fichier, 'rb') as file:
        url_list = pickle.load(file)
    create_file_subtitle(url_list)
main()
