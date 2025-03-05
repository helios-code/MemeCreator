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
        default_hashtags = ["#LARROGANCE", "#meme", "#humour", "#satire"]
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
                # Version économique du prompt
                system_content = "Génère uniquement des hashtags pour un mème humoristique."
                user_content = f"Pour un mème sur '{subject}' avec la punchline: '{punchline}', génère 3-5 hashtags pertinents et populaires. Réponds uniquement avec les hashtags, un par ligne, au format #hashtag."
                model = "gpt-3.5-turbo"
                max_tokens = 100
            else:
                # Version complète du prompt
                system_content = "Tu es un expert en marketing de contenu humoristique sur les réseaux sociaux. Tu génères des hashtags percutants pour des mèmes satiriques."
                user_content = f"Je viens de créer un mème 'L'ARROGANCE!' sur le sujet '{subject}' avec la punchline suivante:\n\n'{punchline}'\n\nGénère 5-7 hashtags pertinents et populaires. Réponds uniquement avec les hashtags, un par ligne, au format #hashtag."
                model = "gpt-4"
                max_tokens = 150
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=max_tokens,
                temperature=0.7
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
                # Version économique du prompt
                system_content = "Tu es un expert en marketing de contenu humoristique. Génère une description courte et percutante."
                user_content = f"Pour un mème satirique 'L'ARROGANCE!' sur '{subject}' avec la punchline: '{punchline}', génère une description engageante (max 100 caractères) qui explique la blague et incite au partage. Sois direct et provocant."
                model = "gpt-3.5-turbo"
                max_tokens = 100
            else:
                # Version complète du prompt
                system_content = "Tu es un expert en marketing de contenu humoristique sur les réseaux sociaux. Tu génères des descriptions engageantes pour des mèmes satiriques qui maximisent l'engagement et les partages."
                user_content = f"Je viens de créer un mème 'L'ARROGANCE!' sur le sujet '{subject}' avec la punchline suivante:\n\n'{punchline}'\n\nGénère une description engageante (100-150 caractères) qui:\n1. Explique subtilement la blague sans la gâcher\n2. Utilise un ton provocant qui incite au débat\n3. Inclut un appel à l'action implicite pour le partage\n\nLa description doit être percutante et faire sourire."
                model = "gpt-4"
                max_tokens = 200
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=max_tokens,
                temperature=0.7
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
                system_content = "Génère des punchlines satiriques courtes et percutantes sur le sujet donné, en utilisant la structure 'Quand X fait Y, mais quand lui Z'."
                user_content = f"Crée une punchline satirique sur {current_subject} en utilisant la structure 'Quand X fait Y, mais quand lui Z'. Mets en évidence une forte contradiction ou hypocrisie. Sois direct et provocant."
                model = "gpt-3.5-turbo"
                max_tokens = 40
                temperature = 0.8
            else:
                # Version complète du prompt
                system_content = "Tu es un générateur de punchlines satiriques et ultra-clivantes sur la politique et la société. Ton objectif est de produire des phrases courtes, percutantes et polarisantes, qui accentuent les contradictions et les absurdités des différents courants idéologiques et événements actuels. Tu DOIS utiliser la structure 'Quand X fait Y, mais quand lui Z' pour mettre en évidence une forte contradiction. L'humour doit être extrêmement sarcastique, provocant et basé sur des débats d'actualité. Tes punchlines seront utilisées sur des mèmes vidéos où Ludovic Magnin crie 'L'ARROGANCE !'."
                
                # Remplacer la variable {subject} dans le prompt utilisateur
                user_content = "Génère une punchline humoristique et clivante sur le sujet suivant : **{subject}**.\n\n⚠️ DIRECTIVES :\n- La punchline DOIT suivre la structure 'Quand X fait Y, mais quand lui Z' ou une variante similaire qui met en évidence une contradiction.\n- Elle doit être courte (10-20 mots max).\n- Elle doit être frontalement partisane (soit anti-gauche, soit anti-droite, soit contre une tendance sociétale précise, mais jamais neutre).\n- L'humour doit être basé sur une exagération des paradoxes politiques ou sociaux liés au sujet.\n- La phrase doit être immédiatement compréhensible et provoquer une forte réaction.\n\n🎯 **Exemples de structure à suivre** :\n- 'Quand un UDC critique les étrangers, mais embauche 10 frontaliers dans son entreprise.'\n- 'Quand un écolo prône la sobriété, mais part en vacances en jet privé.'\n- 'Quand un banquier parle d'éthique, mais cache l'argent de ses clients aux Caïmans.'\n\n📌 **Format de réponse attendu :**\n- Une seule punchline bien travaillée suivant la structure demandée.\n- Aucun texte d'introduction ou d'explication, uniquement la phrase brute et percutante.\n\n📝 **Sujet actuel :** {subject}"
                user_content = user_content.replace("{subject}", current_subject)
                model = "gpt-4"
                max_tokens = 50
                temperature = 0.7
            
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