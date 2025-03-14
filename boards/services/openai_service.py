import openai
from django.conf import settings

class OpenAIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    async def optimize_description(self, prompt):
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that optimizes task descriptions to be more clear, concise, and actionable."},
                    {"role": "user", "content": f"Please optimize this task description: {prompt}"}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            raise Exception("Failed to optimize description") 