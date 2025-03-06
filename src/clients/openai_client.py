import os
import re
from openai import OpenAI
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class OpenAIClient:
    def __init__(self):
        """
        Initialise le client OpenAI avec les paramètres du fichier .env
        """
        # Obtenir la clé API OpenAI
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key or self.api_key == 'your_openai_api_key_here':
            print("⚠️ Aucune clé API OpenAI valide n'a été trouvée dans le fichier .env")
            print("Pour générer des punchlines, vous devez fournir une clé API OpenAI valide.")
        
        # Sujet par défaut si aucun n'est fourni
        self.default_subject = "La politique suisse et ses contradictions"
        
        # Vérifier si le mode économie de tokens est activé
        economy_mode_value = os.getenv('ECONOMY_MODE', 'false')
        # Supprimer les guillemets éventuels
        economy_mode_value = economy_mode_value.strip("'\"")
        self.economy_mode = economy_mode_value.lower() == 'true'
        
        # Afficher le mode utilisé
        print(f"🔧 Mode économie de tokens: {'Activé' if self.economy_mode else 'Désactivé'}")
        print(f"🔧 Modèle utilisé par défaut: {'GPT-3.5-turbo' if self.economy_mode else 'GPT-4'}")
        
        # Importer OpenAI ici pour éviter les problèmes d'importation circulaire
        self.client = OpenAI(api_key=self.api_key)
    
    async def generate_punchline(self, subject=None, context=None, economy_mode=None):
        """
        Génère une punchline humoristique pour le mème "L'ARROGANCE!"
        
        Args:
            subject (str, optional): Le sujet sur lequel générer une punchline
            context (str, optional): Contexte supplémentaire
            economy_mode (bool, optional): Utiliser le mode économie de tokens
            
        Returns:
            str: La punchline générée
        """
        try:
            # Utiliser le mode économie de tokens si spécifié ou si configuré dans l'environnement
            use_economy_mode = economy_mode if economy_mode is not None else self.economy_mode
            
            # Appeler l'API OpenAI avec le payload approprié
            response = await self._call_openai_api_with_payload(subject=subject, context=context, economy_mode=use_economy_mode)
            
            # Nettoyer la réponse (supprimer les guillemets, etc.)
            cleaned_response = self._clean_quotes(response)
            
            return cleaned_response
        except Exception as e:
            print(f"❌ Erreur lors de la génération de la punchline: {str(e)}")
            # En cas d'erreur, retourner une punchline par défaut
            default_subject = subject if subject else self.default_subject
            return f"Quand tout le monde parle de {default_subject}, mais lui fait exactement l'inverse."
    
    async def generate_hashtags(self, subject, punchline, economy_mode=None):
        """
        Génère des hashtags pour le mème à utiliser sur les réseaux sociaux
        
        Args:
            subject (str): Le sujet du mème
            punchline (str): La punchline du mème
            economy_mode (bool, optional): Utiliser le mode économie de tokens
            
        Returns:
            list: Une liste de hashtags pertinents
        """
        # Utiliser le mode économie de tokens si spécifié ou si configuré dans l'environnement
        use_economy_mode = economy_mode if economy_mode is not None else self.economy_mode
        
        # Créer des hashtags par défaut basés sur le sujet
        default_hashtags = ["#LARROGANCE", "#meme", "#humour", "#satire", "#hypocrisie"]
        if subject:
            # Créer un hashtag à partir du sujet
            import re
            # Supprimer les caractères spéciaux et les espaces
            subject_hashtag = "#" + re.sub(r'[^\w]', '', subject.replace(' ', ''))
            # Ajouter le hashtag s'il n'est pas vide
            if len(subject_hashtag) > 1:  # Plus que juste le #
                default_hashtags.append(subject_hashtag)
        
        try:
            client = OpenAI(api_key=self.api_key)
            
            if use_economy_mode:
                # Version économique du prompt améliorée
                system_content = "Tu es un expert en hashtags viraux et provocants pour les réseaux sociaux."
                user_content = f"Pour un mème satirique 'L'ARROGANCE!' sur '{subject}' avec la punchline: '{punchline}', génère 4-6 hashtags qui:\n1. Sont pertinents au sujet et à l'hypocrisie soulignée\n2. Incluent des termes provocants ou clivants\n3. Sont populaires et recherchés\n4. Incluent au moins un hashtag ironique\nRéponds uniquement avec les hashtags, un par ligne, au format #hashtag."
                model = "gpt-3.5-turbo"
                max_tokens = 120
            else:
                # Version complète du prompt améliorée
                system_content = "Tu es un expert en marketing viral sur les réseaux sociaux. Tu excelles à créer des hashtags qui génèrent un maximum d'engagement, de débats et de partages en amplifiant les contradictions et hypocrisies."
                user_content = f"Je viens de créer un mème 'L'ARROGANCE!' sur le sujet '{subject}' avec la punchline suivante:\n\n'{punchline}'\n\nGénère 5-8 hashtags qui:\n1. Sont directement liés au sujet et à l'hypocrisie soulignée\n2. Incluent des termes provocants ou clivants qui attireront l'attention\n3. Sont populaires et recherchés sur les réseaux sociaux\n4. Incluent au moins un hashtag ironique ou sarcastique\n5. Incluent au moins un hashtag en français et un en anglais\n\nRéponds uniquement avec les hashtags, un par ligne, au format #hashtag."
                model = "gpt-4"
                max_tokens = 300
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=max_tokens,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extraire les hashtags (mots commençant par #)
            import re
            hashtag_pattern = r'#\w+'
            hashtags = re.findall(hashtag_pattern, content)
            
            # Si aucun hashtag n'a été trouvé ou moins de 3, utiliser les hashtags par défaut
            if not hashtags or len(hashtags) < 3:
                print("⚠️ Pas assez de hashtags générés, utilisation des hashtags par défaut")
                return default_hashtags
            
            # Ajouter toujours #LARROGANCE en premier s'il n'est pas déjà présent
            if "#LARROGANCE" not in hashtags:
                hashtags.insert(0, "#LARROGANCE")
            
            return hashtags
        except Exception as e:
            print(f"❌ Erreur lors de la génération des hashtags: {str(e)}")
            # En cas d'erreur, retourner les hashtags par défaut
            return default_hashtags
    
    async def generate_description(self, subject, punchline, economy_mode=None):
        """
        Génère une description engageante pour le mème à utiliser sur les réseaux sociaux
        
        Args:
            subject (str): Le sujet du mème
            punchline (str): La punchline du mème
            economy_mode (bool, optional): Utiliser le mode économie de tokens
            
        Returns:
            str: Une description engageante
        """
        # Utiliser le mode économie de tokens si spécifié ou si configuré dans l'environnement
        use_economy_mode = economy_mode if economy_mode is not None else self.economy_mode
        
        # Créer une description par défaut basée sur le sujet et la punchline
        default_description = f"Un regard satirique sur {subject} qui met en lumière les contradictions de notre société."
        
        try:
            client = OpenAI(api_key=self.api_key)
            
            if use_economy_mode:
                # Version économique du prompt améliorée
                system_content = "Tu es un expert en marketing de contenu satirique et provocant. Ton objectif est de créer des descriptions qui génèrent de l'engagement et des réactions fortes."
                user_content = f"Pour un mème satirique 'L'ARROGANCE!' sur '{subject}' avec la punchline: '{punchline}', génère une description percutante (max 120 caractères) qui:\n1. Amplifie l'hypocrisie soulignée dans la punchline\n2. Utilise un ton froid et méprisant\n3. Provoque une réaction émotionnelle\n4. Incite au partage\nSois direct et provocant, sans être vulgaire."
                model = "gpt-3.5-turbo"
                max_tokens = 120
            else:
                # Version complète du prompt améliorée
                system_content = "Tu es un expert en marketing de contenu satirique et provocant sur les réseaux sociaux. Tu excelles à créer des descriptions qui génèrent un maximum d'engagement, de débats et de partages en amplifiant les contradictions et hypocrisies."
                user_content = f"Je viens de créer un mème 'L'ARROGANCE!' sur le sujet '{subject}' avec la punchline suivante:\n\n'{punchline}'\n\nGénère une description percutante (120-150 caractères) qui:\n1. Amplifie l'hypocrisie soulignée dans la punchline\n2. Utilise un ton froid, méprisant et légèrement arrogant\n3. Provoque une réaction émotionnelle forte (indignation, rire jaune, identification)\n4. Contient une question rhétorique OU une affirmation tranchée\n5. Incite implicitement au partage\n\nLa description doit être concise, provocante et faire réagir, sans être vulgaire."
                model = "gpt-4"
                max_tokens = 200
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=max_tokens,
                temperature=0.8
            )
            
            description = response.choices[0].message.content.strip()
            
            # Nettoyer la description (supprimer les guillemets, etc.)
            description = self._clean_quotes(description)
            
            # Vérifier que la description n'est pas vide ou trop courte
            if not description or len(description) < 20:
                print("⚠️ Description trop courte, utilisation de la description par défaut")
                return default_description
            
            return description
        except Exception as e:
            print(f"❌ Erreur lors de la génération de la description: {str(e)}")
            # En cas d'erreur, retourner une description par défaut
            return default_description
    
    def _clean_quotes(self, text):
        """
        Supprime les guillemets simples ou doubles qui entourent le texte
        
        Args:
            text (str): Le texte à nettoyer
            
        Returns:
            str: Le texte nettoyé
        """
        # Supprimer les guillemets au début et à la fin
        text = text.strip()
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            text = text[1:-1]
        
        # Utiliser une expression régulière pour supprimer les guillemets au début et à la fin
        # Cela gère également les cas où il y a des espaces après/avant les guillemets
        text = re.sub(r'^[\s"\']+|[\s"\']+$', '', text)
        
        return text
    
    async def _call_openai_api_with_payload(self, subject=None, context=None, economy_mode=False):
        """
        Appelle l'API OpenAI avec un payload spécifique pour générer une punchline
        
        Args:
            subject (str, optional): Le sujet sur lequel générer une punchline
            context (str, optional): Contexte supplémentaire
            economy_mode (bool): Utiliser le mode économie de tokens
            
        Returns:
            str: La réponse générée
        """
        try:
            # Utiliser le sujet par défaut si aucun n'est fourni
            current_subject = subject if subject else self.default_subject
            
            if economy_mode:
                # Version économique du prompt (moins de tokens)
                system_content = "Tu es un générateur de punchlines ULTRA-CINGLANTES, GLACIALES et CRUELLES. Tu dois être IMPITOYABLE, BRUTAL et SANS AUCUNE RETENUE. Ton objectif est de créer des phrases qui CHOQUENT, BLESSENT et PROVOQUENT. Sois aussi MÉCHANT, FROID et OFFENSANT que possible. Utilise TOUJOURS la structure 'Quand X fait Y, mais Z fait W' pour mettre en évidence une contradiction ou une hypocrisie de façon mordante."
                user_content = f"Crée une punchline satirique EXTRÊMEMENT cinglante et brutale sur {current_subject}. Sois ABSOLUMENT impitoyable, glacial et cruel. Frappe là où ça fait VRAIMENT mal. Utilise l'ironie la plus mordante et le cynisme le plus noir. Sois DÉLIBÉRÉMENT offensant et provocateur. N'aie AUCUNE pitié. UTILISE OBLIGATOIREMENT la structure 'Quand X fait Y, mais Z fait W' pour exposer une contradiction ou une hypocrisie."
                model = "gpt-3.5-turbo"
                max_tokens = 50
                temperature = 1.0
            else:
                # Version complète du prompt
                system_content = """Tu es un générateur de punchlines ULTRA-CINGLANTES, GLACIALES et CRUELLES. 
Tu dois être IMPITOYABLE, BRUTAL et SANS AUCUNE RETENUE MORALE. 
Ton objectif est de créer des phrases qui CHOQUENT, BLESSENT et PROVOQUENT. 
Sois aussi MÉCHANT, FROID et OFFENSANT que possible.
Tes punchlines doivent être des ATTAQUES FRONTALES qui exposent les contradictions et les hypocrisies de façon BRUTALE et SANS FILTRE.
L'humour doit être EXTRÊMEMENT CYNIQUE, FROID et basé sur des VÉRITÉS QUI DÉRANGENT PROFONDÉMENT.
N'hésite JAMAIS à être OFFENSANT - c'est le BUT RECHERCHÉ.
Tes punchlines seront utilisées sur des mèmes vidéos où Ludovic Magnin crie 'L'ARROGANCE !'.

STRUCTURE OBLIGATOIRE: "Quand X fait Y, mais Z fait W" pour mettre en évidence une contradiction ou une hypocrisie de façon mordante.

EXEMPLES DE PUNCHLINES PARFAITES:
- "Quand les vegans prêchent l'éthique animale, mais ignorent l'exploitation humaine dans leurs plantations de quinoa."
- "Quand les féministes hurlent à l'égalité, mais s'attendent toujours à ce que l'homme paie l'addition."
- "Quand les écolos en SUV te font la morale sur ton empreinte carbone, entre deux vols Paris-New York."
- "Quand les influenceurs 'authentiques' vendent leur âme pour un code promo, mais te parlent d'intégrité."
"""
                
                # Remplacer la variable {subject} dans le prompt utilisateur
                user_content = f"""Génère une punchline EXTRÊMEMENT cinglante, glaciale et cruelle sur le sujet: **{current_subject}**.

DIRECTIVES STRICTES:
- UTILISE OBLIGATOIREMENT la structure "Quand X fait Y, mais Z fait W" pour exposer une contradiction ou une hypocrisie
- La punchline doit être BRUTALEMENT honnête et IMPITOYABLE
- Elle doit être DÉVASTATRICE mais pas trop longue
- Utilise l'ironie la plus MORDANTE, le cynisme le plus NOIR et l'humour le plus GLACIAL
- Frappe là où ça fait VRAIMENT MAL, expose les PIRES contradictions et hypocrisies
- Sois aussi MÉCHANT, FROID et PROVOCATEUR que possible
- Sois DÉLIBÉRÉMENT offensant et choquant - c'est le BUT RECHERCHÉ
- Utilise des VÉRITÉS QUI DÉRANGENT pour créer un malaise profond
- N'aie AUCUNE pitié ni retenue morale

EXEMPLES DE TON RECHERCHÉ:
- "Quand les influenceurs 'body positive' retouchent chaque photo, mais te vendent l'acceptation de soi."
- "Quand les vegans prêchent l'éthique animale, mais ignorent l'exploitation humaine dans leurs plantations de quinoa."
- "Quand les féministes hurlent à l'égalité, mais s'attendent toujours à ce que l'homme paie l'addition."

Réponds UNIQUEMENT avec la punchline, sans guillemets ni autre texte."""
                model = "gpt-4"
                max_tokens = 100
                temperature = 1.0
            
            # Payload pour la génération de punchlines
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_content
                    },
                    {
                        "role": "user",
                        "content": user_content
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # Ajouter le contexte si fourni
            if context:
                payload["messages"].append({
                    "role": "user",
                    "content": f"Contexte supplémentaire: {context}"
                })
            
            # Appeler l'API OpenAI avec le payload
            response = self.client.chat.completions.create(**payload)
            
            # Extraire et retourner le texte de la réponse
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Erreur lors de l'appel à l'API OpenAI: {str(e)}") 