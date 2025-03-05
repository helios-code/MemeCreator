import os
import uuid
from datetime import datetime
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class VideoProcessor:
    def __init__(self):
        # Obtenir le chemin absolu du répertoire courant
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Obtenir les chemins depuis les variables d'environnement ou utiliser des valeurs par défaut
        template_path_env = os.getenv('TEMPLATE_VIDEO_PATH', 'template.mp4')
        
        # Convertir en chemin absolu si nécessaire
        if not os.path.isabs(template_path_env):
            self.template_path = os.path.join(current_dir, os.path.basename(template_path_env))
        else:
            self.template_path = template_path_env
        
        # Chemin du dossier de sortie
        output_dir_env = os.getenv('OUTPUT_DIRECTORY', 'output')
        if not os.path.isabs(output_dir_env):
            self.output_dir = os.path.join(os.path.dirname(current_dir), output_dir_env)
        else:
            self.output_dir = output_dir_env
        
        # Autres paramètres
        self.font = os.getenv('FONT_PATH', 'Arial')
        self.font_size = int(os.getenv('FONT_SIZE', '40'))
        self.text_color = os.getenv('TEXT_COLOR', 'white')
        # Forcer la position du texte à 35% de la hauteur (environ 250px sur une vidéo 720p)
        self.text_position_y = 0.19  # Valeur forcée pour placer le texte plus bas
        self.text_margin_x = float(os.getenv('TEXT_MARGIN_X', '0.02'))      # 1% de marge de chaque côté
        self.text_bg = os.getenv('TEXT_BACKGROUND', 'black')
        
        # Créer le dossier de sortie s'il n'existe pas
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Vérifier que le fichier template existe
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"Le fichier template {self.template_path} n'existe pas")
        
        # Vérifier que le fichier est une vidéo valide
        try:
            with VideoFileClip(self.template_path) as clip:
                if not hasattr(clip, 'duration') or clip.duration <= 0:
                    raise ValueError(f"Le fichier vidéo {self.template_path} n'a pas de durée valide")
                print(f"📂 Vidéo template valide: {self.template_path} (durée: {clip.duration:.2f}s)")
        except Exception as e:
            raise ValueError(f"Erreur lors de la vérification du fichier vidéo: {str(e)}")
        
        print(f"📂 Utilisation du template: {self.template_path}")
        print(f"📂 Dossier de sortie: {self.output_dir}")
    
    async def create_meme(self, text):
        """
        Crée un mème vidéo en ajoutant le texte sur la vidéo template
        
        Args:
            text (str): Le texte à ajouter sur la vidéo
            
        Returns:
            str: Le chemin du fichier vidéo généré
        """
        try:
            # Charger la vidéo template
            print(f"🎬 Chargement de la vidéo template: {self.template_path}")
            video = VideoFileClip(self.template_path)
            
            # Vérifier que la vidéo a une durée valide
            if not hasattr(video, 'duration') or video.duration <= 0:
                raise ValueError(f"La vidéo n'a pas de durée valide")
            
            # Créer le clip de texte
            print(f"📝 Création du clip de texte avec le texte: \"{text}\"")
            text_clip = self._create_text_clip(text, video.size)
            
            # Superposer le texte sur la vidéo
            print(f"🔄 Superposition du texte sur la vidéo...")
            final_clip = CompositeVideoClip([video, text_clip])
            
            # Définir explicitement la durée du clip final
            final_clip = final_clip.set_duration(video.duration)
            
            # Générer un nom de fichier unique
            output_filename = self._generate_output_filename()
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Exporter la vidéo
            print(f"💾 Exportation de la vidéo vers: {output_path}")
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Fermer les clips pour libérer les ressources
            video.close()
            text_clip.close()
            final_clip.close()
            
            return output_path
        except Exception as e:
            print(f"❌ Erreur lors de la création du mème: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Erreur lors de la création du mème: {str(e)}")
            
    def _create_text_clip(self, text, video_size):
        """
        Crée un clip de texte avec un fond
        
        Args:
            text (str): Le texte à afficher
            video_size (tuple): La taille de la vidéo (largeur, hauteur)
            
        Returns:
            TextClip: Le clip de texte
        """
        try:
            width, height = video_size
            
            # Calculer la position y du texte
            position_y = height * self.text_position_y
            
            # Calculer la largeur du texte avec les marges
            text_width = width * (1 - 2 * self.text_margin_x)
            
            # Créer le clip de texte avec un fond
            text_clip = TextClip(
                text,
                font=self.font,
                fontsize=self.font_size,
                color=self.text_color,
                bg_color=self.text_bg,
                method='caption',
                align='center',
                size=(text_width, None),
                stroke_color='black',
                stroke_width=1
            )
            
            # Positionner le texte en haut de la vidéo
            margin_x = width * self.text_margin_x
            text_clip = text_clip.set_position((margin_x, position_y))
            
            return text_clip
        except Exception as e:
            print(f"❌ Erreur lors de la création du clip de texte: {str(e)}")
            # Créer un clip de texte d'erreur
            error_clip = TextClip(
                "Erreur de texte",
                font=self.font,
                fontsize=self.font_size,
                color='red',
                bg_color='black',
                method='caption',
                align='center',
                size=(video_size[0] * 0.8, None)
            )
            error_clip = error_clip.set_position(('center', 50))
            return error_clip
    
    def _generate_output_filename(self):
        """
        Génère un nom de fichier unique pour la vidéo de sortie
        
        Returns:
            str: Le nom du fichier
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"arrogance_meme_{timestamp}_{unique_id}.mp4" 