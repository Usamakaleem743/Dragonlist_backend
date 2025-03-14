from openai import AsyncOpenAI
from django.conf import settings

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def optimize_description(self, prompt):
        try:
            print("Attempting to optimize description with OpenAI")
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": f"Please Give me a summary of this task: {prompt}"
                }],
                temperature=0.7,
                max_tokens=150
            )
            
            if response.choices:
                print("Successfully optimized description")
                return response.choices[0].message.content
                
            return "Could not generate optimized description."
                
        except Exception as e:
            print(f"OpenAI Service Error: {str(e)}")
            return "I'm sorry, I couldn't optimize the description at the moment. Please try again later." 