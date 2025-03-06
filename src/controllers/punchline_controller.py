from models.punchline_model import PunchlineModel
from typing import Dict, List, Any, Optional, Tuple
import logging
import os
from openai import OpenAI
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('punchline_controller')

class PunchlineController:
    """
    Controller for handling punchline generation and evaluation logic.
    """
    
    def __init__(self):
        """Initialize the punchline controller with model and OpenAI client."""
        self.model = PunchlineModel()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        
        # Default number of candidates to generate
        self.default_num_candidates = int(os.getenv('DEFAULT_NUM_CANDIDATES', '3'))
        
        # Default quality threshold
        self.default_quality_threshold = float(os.getenv('DEFAULT_QUALITY_THRESHOLD', '0.7'))
        
        logger.info("Punchline controller initialized")
    
    async def get_best_punchline(
        self, 
        subject: str, 
        economy_mode: bool = False,
        threshold: Optional[float] = None,
        num_candidates: Optional[int] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate and evaluate punchlines, returning the best one.
        
        Args:
            subject: The subject to generate punchlines about
            economy_mode: Whether to use economy mode (fewer tokens)
            threshold: Quality threshold (default from env or 0.7)
            num_candidates: Number of candidates to generate (default from env or 3)
            
        Returns:
            Tuple[str, Dict]: The best punchline and its metadata
        """
        try:
            # Set defaults if not provided
            if threshold is None:
                threshold = self.default_quality_threshold
                
            if num_candidates is None:
                num_candidates = self.default_num_candidates
            
            # Generate candidate punchlines
            logger.info(f"Generating {num_candidates} candidate punchlines for subject: '{subject}'")
            candidates = await self._generate_candidate_punchlines(subject, num_candidates, economy_mode)
            
            # Evaluate each punchline
            logger.info("Evaluating candidate punchlines")
            evaluated_punchlines = []
            
            for punchline in candidates:
                # Clean the punchline
                cleaned_punchline = self._clean_punchline(punchline)
                
                # Evaluate the punchline
                evaluation = await self._evaluate_punchline(subject, cleaned_punchline)
                
                # Calculate overall score
                overall_score = self._calculate_overall_score(evaluation)
                
                # Store the evaluation
                self.model.store_evaluation(cleaned_punchline, subject, evaluation, overall_score)
                
                # Add to evaluated punchlines
                evaluated_punchlines.append({
                    'text': cleaned_punchline,
                    'evaluation': evaluation,
                    'overall_score': overall_score
                })
            
            # Filter by quality threshold
            quality_punchlines = [p for p in evaluated_punchlines if p['overall_score'] >= threshold]
            
            if not quality_punchlines:
                # If no punchlines meet the threshold, take the best one
                logger.warning(f"No punchlines met the quality threshold of {threshold}. Using the best available.")
                best_punchline = max(evaluated_punchlines, key=lambda x: x['overall_score'])
            else:
                # Take the best punchline that meets the threshold
                best_punchline = max(quality_punchlines, key=lambda x: x['overall_score'])
            
            # Mark the best punchline as selected
            self.model.mark_as_selected(best_punchline['text'])
            
            # Create metadata
            metadata = {
                'evaluation': best_punchline['evaluation'],
                'overall_score': best_punchline['overall_score']
            }
            
            logger.info(f"Selected best punchline with score {best_punchline['overall_score']:.2f}: \"{best_punchline['text']}\"")
            
            return best_punchline['text'], metadata
        except Exception as e:
            logger.error(f"Error getting best punchline: {str(e)}")
            raise
    
    async def _generate_candidate_punchlines(
        self, 
        subject: str, 
        num_candidates: int = 3,
        economy_mode: bool = False
    ) -> List[str]:
        """
        Generate candidate punchlines for a given subject.
        
        Args:
            subject: The subject to generate punchlines about
            num_candidates: Number of candidates to generate
            economy_mode: Whether to use economy mode (fewer tokens)
            
        Returns:
            List[str]: List of candidate punchlines
        """
        try:
            # Select model based on economy mode
            model = "gpt-3.5-turbo" if economy_mode else "gpt-4"
            
            # Create the prompt
            prompt = self._create_generation_prompt(subject, num_candidates, economy_mode)
            
            # Call OpenAI API - remove await as the client is synchronous
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Tu es un humoriste satirique français spécialisé dans l'humour noir et provocateur."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=1000
            )
            
            # Extract punchlines from response
            content = response.choices[0].message.content
            
            # Parse the response to extract punchlines
            punchlines = self._parse_punchlines_from_response(content, num_candidates)
            
            logger.info(f"Generated {len(punchlines)} candidate punchlines")
            return punchlines
            
        except Exception as e:
            logger.error(f"Error generating candidate punchlines: {str(e)}")
            raise
    
    def _create_generation_prompt(self, subject: str, num_candidates: int, economy_mode: bool) -> str:
        """
        Create a prompt for punchline generation.
        
        Args:
            subject: The subject to generate punchlines about
            num_candidates: Number of candidates to generate
            economy_mode: Whether to use economy mode (fewer tokens)
            
        Returns:
            str: The generation prompt
        """
        if economy_mode:
            # Simpler prompt for economy mode
            return f"""Génère {num_candidates} punchlines EXTRÊMEMENT satiriques et choquantes sur "{subject}" en utilisant STRICTEMENT le format "Quand X fait/veut/exige Y mais fait Z (le contraire)".
            
Chaque punchline doit:
- Commencer OBLIGATOIREMENT par "Quand" 
- Mettre en évidence une HYPOCRISIE FLAGRANTE (faire/vouloir une chose mais faire exactement le contraire)
- Être TRÈS MÉCHANTE, FROIDE et CHOQUANTE
- Être courte et percutante (max 100 caractères)
- Viser à provoquer et choquer le lecteur

Exemples de format EXACT à suivre:
- "Quand tu prêches l'égalité mais que tu paies tes stagiaires au lance-pierre"
- "Quand tu exiges du respect mais que tu insultes tes collègues dès qu'ils ont le dos tourné"
- "Quand tu défends l'environnement mais que tu changes d'iPhone tous les 6 mois"

Le ton doit être GLACIAL, MÉPRISANT et PROVOCATEUR.
TOUJOURS commencer par "Quand" et mettre en évidence une contradiction flagrante.

Format: Numérote chaque punchline (1., 2., etc.)"""
        else:
            # Full prompt for normal mode
            return f"""Génère {num_candidates} punchlines EXTRÊMEMENT satiriques et choquantes sur "{subject}" pour un mème vidéo intitulé "L'ARROGANCE" en utilisant STRICTEMENT le format "Quand X fait/veut/exige Y mais fait Z (le contraire)".
            
Chaque punchline doit:
- Commencer OBLIGATOIREMENT par "Quand" 
- Mettre en évidence une HYPOCRISIE FLAGRANTE (faire/vouloir une chose mais faire exactement le contraire)
- Être TRÈS MÉCHANTE, FROIDE et CHOQUANTE
- Être courte et percutante (idéalement moins de 100 caractères)
- Viser à provoquer et choquer le lecteur
- Avoir un ton glacial et méprisant
- Être cinglante et sans pitié

Exemples de format EXACT à suivre:
- "Quand tu prêches l'égalité mais que tu paies tes stagiaires au lance-pierre"
- "Quand tu exiges du respect mais que tu insultes tes collègues dès qu'ils ont le dos tourné"
- "Quand tu défends l'environnement mais que tu changes d'iPhone tous les 6 mois"

Le ton doit être GLACIAL, MÉPRISANT et PROVOCATEUR.
TOUJOURS commencer par "Quand" et mettre en évidence une contradiction flagrante.

Évite:
- Les formulations trop douces ou politiquement correctes
- L'humour léger ou bienveillant
- Les critiques voilées ou subtiles

Format: Numérote chaque punchline (1., 2., etc.) et ne donne que les punchlines, sans explication."""
    
    def _parse_punchlines_from_response(self, content: str, expected_count: int) -> List[str]:
        """
        Parse punchlines from the OpenAI response.
        
        Args:
            content: The response content
            expected_count: Expected number of punchlines
            
        Returns:
            List[str]: List of parsed punchlines
        """
        # Try to extract numbered punchlines
        pattern = r'(?:^|\n)(?:\d+\.\s*|\-\s*)(.*?)(?:\n|$)'
        matches = re.findall(pattern, content)
        
        # Clean up the matches
        punchlines = [match.strip().strip('"\'') for match in matches if match.strip()]
        
        # If we didn't get the expected number, try a different approach
        if len(punchlines) < expected_count:
            # Split by newlines and filter out empty lines
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Remove numbering if present
            cleaned_lines = []
            for line in lines:
                # Remove numbering patterns like "1. " or "- "
                cleaned_line = re.sub(r'^(?:\d+\.\s*|\-\s*)', '', line).strip().strip('"\'')
                if cleaned_line:
                    cleaned_lines.append(cleaned_line)
            
            # Use these lines if we got more than before
            if len(cleaned_lines) > len(punchlines):
                punchlines = cleaned_lines
        
        return punchlines
    
    async def _evaluate_punchline(self, subject: str, punchline: str) -> Dict[str, float]:
        """
        Evaluate a punchline using OpenAI.
        
        Args:
            subject: The subject of the punchline
            punchline: The punchline to evaluate
            
        Returns:
            Dict[str, float]: Evaluation criteria scores
        """
        try:
            # Create the evaluation prompt
            prompt = self._create_evaluation_prompt(subject, punchline)
            
            # Call OpenAI API - remove await as the client is synchronous
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Tu es un expert en humour satirique qui évalue la qualité des punchlines."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            # Extract evaluation from response
            content = response.choices[0].message.content
            
            # Parse the evaluation
            evaluation = self._parse_evaluation_from_response(content)
            
            return evaluation
        except Exception as e:
            logger.error(f"Error evaluating punchline: {str(e)}")
            # Return default evaluation
            return {
                'cruaute': 0.5,
                'provocation': 0.5,
                'pertinence': 0.5,
                'concision': 0.5,
                'impact': 0.5
            }
    
    def _create_evaluation_prompt(self, subject: str, punchline: str) -> str:
        """
        Create a prompt for punchline evaluation.
        
        Args:
            subject: The subject of the punchline
            punchline: The punchline to evaluate
            
        Returns:
            str: The evaluation prompt
        """
        return f"""Évalue la punchline suivante sur le sujet "{subject}":

"{punchline}"

Évalue chaque critère sur une échelle de 0 à 1 (0 = très mauvais, 1 = excellent):

1. Cruauté: À quel point la punchline est cruelle et mordante?
2. Provocation: À quel point la punchline est provocatrice et audacieuse?
3. Pertinence: À quel point la punchline est pertinente par rapport au sujet?
4. Concision: À quel point la punchline est concise et directe?
5. Impact: À quel point la punchline a un impact fort et mémorable?

Format de réponse:
cruaute: [score]
provocation: [score]
pertinence: [score]
concision: [score]
impact: [score]

Donne uniquement les scores sans explication."""
    
    def _parse_evaluation_from_response(self, content: str) -> Dict[str, float]:
        """
        Parse evaluation scores from the OpenAI response.
        
        Args:
            content: The response content
            
        Returns:
            Dict[str, float]: Evaluation criteria scores
        """
        # Initialize default scores
        evaluation = {
            'cruaute': 0.5,
            'provocation': 0.5,
            'pertinence': 0.5,
            'concision': 0.5,
            'impact': 0.5
        }
        
        # Try to extract scores using regex
        for criterion in evaluation.keys():
            pattern = rf'{criterion}:\s*(\d+(?:\.\d+)?)'
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    score = float(match.group(1))
                    # Ensure score is between 0 and 1
                    score = max(0, min(1, score))
                    evaluation[criterion] = score
                except ValueError:
                    pass
        
        return evaluation
    
    def _calculate_overall_score(self, evaluation: Dict[str, float]) -> float:
        """
        Calculate an overall score from evaluation criteria.
        
        Args:
            evaluation: Dictionary of evaluation criteria scores
            
        Returns:
            float: Overall score
        """
        # Weights for each criterion
        weights = {
            'cruaute': 0.2,
            'provocation': 0.25,
            'pertinence': 0.2,
            'concision': 0.15,
            'impact': 0.2
        }
        
        # Calculate weighted average
        weighted_sum = sum(evaluation.get(criterion, 0) * weight 
                          for criterion, weight in weights.items())
        total_weight = sum(weights.values())
        
        # Return overall score
        return weighted_sum / total_weight
    
    def _clean_punchline(self, text: str) -> str:
        """
        Clean a punchline by removing quotes and extra whitespace.
        
        Args:
            text: The punchline to clean
            
        Returns:
            str: Cleaned punchline
        """
        # Remove quotes
        text = text.strip('"\'')
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def get_evaluation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about punchline evaluations.
        
        Returns:
            Dict: Statistics about punchline evaluations
        """
        return self.model.get_evaluation_stats()
    
    def export_punchlines_for_training(self, output_file: str = None) -> str:
        """
        Export punchlines for training purposes.
        
        Args:
            output_file: Path to the output file
            
        Returns:
            str: Path to the exported file
        """
        return self.model.export_punchlines_for_training(output_file) 