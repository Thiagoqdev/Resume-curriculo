"""
Serviço de IA
Integração com OpenAI e outros serviços de IA
"""
from typing import Dict, Any, List
import json
import openai
import logging
from datetime import datetime

from core.config import settings, ai_settings

logger = logging.getLogger(__name__)


class AIService:
    """Serviço de integração com IA"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.max_tokens = ai_settings.MAX_TOKENS
        self.temperature = ai_settings.TEMPERATURE
    
    async def analyze_resume(self, resume_content: str) -> Dict[str, Any]:
        """Analisar currículo usando IA"""
        try:
            prompt = f"""
            {ai_settings.RESUME_ANALYSIS_PROMPT}
            
            Currículo:
            {resume_content}
            
            Retorne APENAS um JSON válido com a seguinte estrutura:
            {{
                "extractedSkills": [
                    {{
                        "name": "Python",
                        "confidence": 0.95,
                        "matched": true,
                        "category": "Programming Languages"
                    }}
                ],
                "experience": [
                    {{
                        "company": "Empresa XYZ",
                        "position": "Desenvolvedor Senior",
                        "duration": "2 anos",
                        "description": "Descrição das atividades",
                        "relevanceScore": 0.85
                    }}
                ],
                "education": [
                    {{
                        "institution": "Universidade ABC",
                        "degree": "Bacharelado",
                        "field": "Ciência da Computação",
                        "year": "2020"
                    }}
                ],
                "languages": ["Português", "Inglês"],
                "certifications": ["AWS Certified", "Scrum Master"]
            }}
            """
            
            response = await self._call_openai(prompt)
            return self._parse_json_response(response, "resume analysis")
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {e}")
            return self._get_default_resume_analysis()
    
    async def analyze_job_description(self, job_content: str) -> Dict[str, Any]:
        """Analisar descrição da vaga usando IA"""
        try:
            prompt = f"""
            Analise a seguinte descrição de vaga e extraia as informações estruturadas:
            
            Descrição da Vaga:
            {job_content}
            
            Retorne APENAS um JSON válido com a seguinte estrutura:
            {{
                "keyRequirements": ["Python", "React", "SQL"],
                "requiredSkills": ["Desenvolvimento Web", "APIs REST", "Banco de Dados"],
                "experienceLevel": "Senior",
                "education": "Superior Completo",
                "benefits": ["Vale Refeição", "Plano de Saúde"],
                "companyInfo": {{
                    "name": "Nome da Empresa",
                    "industry": "Tecnologia",
                    "size": "Médio Porte"
                }}
            }}
            """
            
            response = await self._call_openai(prompt)
            return self._parse_json_response(response, "job analysis")
            
        except Exception as e:
            logger.error(f"Error analyzing job description: {e}")
            return self._get_default_job_analysis()
    
    async def analyze_compatibility(self, resume_analysis: Dict[str, Any], 
                                  job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analisar compatibilidade entre currículo e vaga"""
        try:
            prompt = f"""
            {ai_settings.COMPATIBILITY_ANALYSIS_PROMPT}
            
            Análise do Currículo:
            {json.dumps(resume_analysis, indent=2, ensure_ascii=False)}
            
            Análise da Vaga:
            {json.dumps(job_analysis, indent=2, ensure_ascii=False)}
            
            Retorne APENAS um JSON válido com a seguinte estrutura:
            {{
                "overallScore": 85.5,
                "categoryScores": {{
                    "skills": 90.0,
                    "experience": 85.0,
                    "education": 80.0,
                    "cultural": 75.0
                }},
                "strengths": [
                    "Forte experiência em Python e desenvolvimento web",
                    "Conhecimento sólido em bancos de dados"
                ],
                "weaknesses": [
                    "Falta experiência com React",
                    "Não possui certificações específicas"
                ],
                "recommendations": [
                    "Destacar projetos com Python no currículo",
                    "Mencionar experiência com APIs REST"
                ],
                "improvementAreas": [
                    {{
                        "area": "Frontend Development",
                        "priority": "high",
                        "suggestions": ["Aprender React", "Estudar TypeScript"]
                    }}
                ]
            }}
            """
            
            response = await self._call_openai(prompt)
            return self._parse_json_response(response, "compatibility analysis")
            
        except Exception as e:
            logger.error(f"Error analyzing compatibility: {e}")
            return self._get_default_compatibility_analysis()
    
    async def generate_cover_letter(self, resume_analysis: Dict[str, Any], 
                                  job_analysis: Dict[str, Any],
                                  customizations: Dict[str, Any]) -> Dict[str, Any]:
        """Gerar carta de apresentação"""
        try:
            tone = customizations.get("tone", "formal")
            length = customizations.get("length", "medium")
            focus_areas = customizations.get("focus_areas", [])
            
            prompt = ai_settings.COVER_LETTER_PROMPT.format(
                tone=tone,
                length=length
            )
            
            prompt += f"""
            
            Análise do Currículo:
            {json.dumps(resume_analysis, indent=2, ensure_ascii=False)}
            
            Análise da Vaga:
            {json.dumps(job_analysis, indent=2, ensure_ascii=False)}
            
            Áreas de Foco: {', '.join(focus_areas) if focus_areas else 'Geral'}
            
            Retorne APENAS um JSON válido com a seguinte estrutura:
            {{
                "subject": "Candidatura para [Posição] - [Seu Nome]",
                "greeting": "Prezados Senhores,",
                "introduction": "Parágrafo de introdução...",
                "body": [
                    "Primeiro parágrafo do corpo...",
                    "Segundo parágrafo do corpo..."
                ],
                "conclusion": "Parágrafo de conclusão...",
                "signature": "Atenciosamente,\\n[Seu Nome]",
                "fullText": "Carta completa formatada..."
            }}
            """
            
            response = await self._call_openai(prompt)
            return self._parse_json_response(response, "cover letter generation")
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return self._get_default_cover_letter()
    
    async def extract_skills_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extrair habilidades de um texto"""
        try:
            prompt = f"""
            Extraia todas as habilidades técnicas e profissionais do seguinte texto:
            
            {text}
            
            Retorne APENAS um JSON válido com array de habilidades:
            {{
                "skills": [
                    {{
                        "name": "Python",
                        "category": "Programming Languages",
                        "confidence": 0.95
                    }},
                    {{
                        "name": "Gestão de Projetos",
                        "category": "Soft Skills",
                        "confidence": 0.80
                    }}
                ]
            }}
            """
            
            response = await self._call_openai(prompt)
            result = self._parse_json_response(response, "skill extraction")
            return result.get("skills", [])
            
        except Exception as e:
            logger.error(f"Error extracting skills: {e}")
            return []
    
    async def suggest_improvements(self, resume_analysis: Dict[str, Any], 
                                 target_role: str) -> List[str]:
        """Sugerir melhorias para o currículo"""
        try:
            prompt = f"""
            Com base na análise do currículo abaixo, sugira melhorias específicas 
            para uma posição de {target_role}:
            
            {json.dumps(resume_analysis, indent=2, ensure_ascii=False)}
            
            Retorne APENAS um JSON válido com sugestões:
            {{
                "suggestions": [
                    "Adicionar mais detalhes sobre projetos com Python",
                    "Incluir métricas de performance nos projetos",
                    "Destacar experiência com metodologias ágeis"
                ]
            }}
            """
            
            response = await self._call_openai(prompt)
            result = self._parse_json_response(response, "improvement suggestions")
            return result.get("suggestions", [])
            
        except Exception as e:
            logger.error(f"Error suggesting improvements: {e}")
            return []
    
    async def _call_openai(self, prompt: str) -> str:
        """Chamar API do OpenAI"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em análise de currículos e recrutamento. Sempre retorne respostas em JSON válido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=ai_settings.TOP_P
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise
    
    def _parse_json_response(self, response: str, operation: str) -> Dict[str, Any]:
        """Parsear resposta JSON da IA"""
        try:
            # Limpar resposta (remover markdown, etc.)
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            return json.loads(cleaned_response.strip())
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response for {operation}: {e}")
            logger.error(f"Raw response: {response}")
            raise ValueError(f"Invalid JSON response from AI for {operation}")
    
    def _get_default_resume_analysis(self) -> Dict[str, Any]:
        """Análise padrão de currículo em caso de erro"""
        return {
            "extractedSkills": [
                {
                    "name": "Análise não disponível",
                    "confidence": 0.0,
                    "matched": False,
                    "category": "Unknown"
                }
            ],
            "experience": [],
            "education": [],
            "languages": [],
            "certifications": []
        }
    
    def _get_default_job_analysis(self) -> Dict[str, Any]:
        """Análise padrão de vaga em caso de erro"""
        return {
            "keyRequirements": [],
            "requiredSkills": [],
            "experienceLevel": "Unknown",
            "education": "Not specified",
            "benefits": [],
            "companyInfo": {
                "name": "Unknown",
                "industry": "Unknown",
                "size": "Unknown"
            }
        }
    
    def _get_default_compatibility_analysis(self) -> Dict[str, Any]:
        """Análise padrão de compatibilidade em caso de erro"""
        return {
            "overallScore": 0.0,
            "categoryScores": {
                "skills": 0.0,
                "experience": 0.0,
                "education": 0.0,
                "cultural": 0.0
            },
            "strengths": ["Análise não disponível"],
            "weaknesses": ["Análise não disponível"],
            "recommendations": ["Tente novamente mais tarde"],
            "improvementAreas": []
        }
    
    def _get_default_cover_letter(self) -> Dict[str, Any]:
        """Carta padrão em caso de erro"""
        return {
            "subject": "Candidatura para Vaga",
            "greeting": "Prezados Senhores,",
            "introduction": "Venho por meio desta manifestar meu interesse na vaga disponível.",
            "body": [
                "Infelizmente não foi possível gerar uma carta personalizada no momento.",
                "Por favor, tente novamente mais tarde."
            ],
            "conclusion": "Agradeço pela atenção e aguardo retorno.",
            "signature": "Atenciosamente,\n[Seu Nome]",
            "fullText": "Carta de apresentação não disponível no momento. Tente novamente mais tarde."
        }
    
    async def analyze_market_trends(self, skills: List[str], industry: str) -> Dict[str, Any]:
        """Analisar tendências do mercado para habilidades específicas"""
        try:
            prompt = f"""
            Analise as tendências do mercado de trabalho para as seguintes habilidades 
            na indústria de {industry}:
            
            Habilidades: {', '.join(skills)}
            
            Retorne APENAS um JSON válido com análise de mercado:
            {{
                "marketDemand": {{
                    "Python": {{
                        "demand": "high",
                        "growth": "increasing",
                        "salaryRange": "R$ 8.000 - R$ 15.000",
                        "opportunities": 1250
                    }}
                }},
                "emergingSkills": ["Docker", "Kubernetes", "Machine Learning"],
                "industryInsights": [
                    "Crescimento de 25% na demanda por desenvolvedores Python",
                    "Foco em automação e IA está aumentando"
                ],
                "recommendations": [
                    "Investir em aprendizado de containerização",
                    "Desenvolver conhecimentos em cloud computing"
                ]
            }}
            """
            
            response = await self._call_openai(prompt)
            return self._parse_json_response(response, "market trends analysis")
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {e}")
            return {
                "marketDemand": {},
                "emergingSkills": [],
                "industryInsights": [],
                "recommendations": []
            }
    
    async def generate_interview_questions(self, job_analysis: Dict[str, Any], 
                                         resume_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gerar perguntas de entrevista baseadas na vaga e currículo"""
        try:
            prompt = f"""
            Gere perguntas de entrevista relevantes baseadas na vaga e currículo:
            
            Análise da Vaga:
            {json.dumps(job_analysis, indent=2, ensure_ascii=False)}
            
            Análise do Currículo:
            {json.dumps(resume_analysis, indent=2, ensure_ascii=False)}
            
            Retorne APENAS um JSON válido com perguntas:
            {{
                "questions": [
                    {{
                        "category": "Technical",
                        "question": "Como você implementaria uma API REST em Python?",
                        "difficulty": "medium",
                        "expectedAnswer": "Resposta esperada resumida..."
                    }},
                    {{
                        "category": "Behavioral",
                        "question": "Conte sobre um projeto desafiador que você liderou",
                        "difficulty": "medium",
                        "expectedAnswer": "Buscar exemplos de liderança e resolução de problemas"
                    }}
                ]
            }}
            """
            
            response = await self._call_openai(prompt)
            result = self._parse_json_response(response, "interview questions")
            return result.get("questions", [])
            
        except Exception as e:
            logger.error(f"Error generating interview questions: {e}")
            return []
