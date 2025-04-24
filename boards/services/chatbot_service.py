from openai import OpenAI
from django.conf import settings
from ..models import Board, List, Card, CardMember, CardDate

class ChatbotService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def get_response(self, user_query, user_id):
        try:
            # Get detailed context about user's boards and cards
            boards = Board.objects.filter(members__id=user_id)
            board_details = []
            
            for board in boards:
                lists = List.objects.filter(board=board)
                cards = Card.objects.filter(list__board=board)
                
                board_info = {
                    'name': board.title,
                    'lists_count': lists.count(),
                    'cards_count': cards.count(),
                    'lists': [{
                        'title': lst.title,
                        'cards': [{
                            'title': card.title,
                            'description': card.description,
                            'due_date': CardDate.objects.filter(card=card).first().due_date if CardDate.objects.filter(card=card).exists() else None
                        } for card in Card.objects.filter(list=lst)]
                    } for lst in lists]
                }
                board_details.append(board_info)

            # Create detailed context for the AI
            context = f"""
            User's Project Information:
            Total Boards: {boards.count()}
            
            Board Details:
            {self._format_board_details(board_details)}
            
            User Query: {user_query}
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a helpful project management assistant with access to the user's board data. 
                        Provide specific insights about their projects, tasks, and deadlines. 
                        Reference actual board names, lists, and cards in your responses when relevant.
                        If there are no cards or boards, suggest creating some and provide examples."""
                    },
                    {
                        "role": "user", 
                        "content": context
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Chatbot Service Error: {str(e)}")
            return "I apologize, but I'm having trouble processing your request right now."

    def _format_board_details(self, board_details):
        formatted_text = ""
        for board in board_details:
            formatted_text += f"\nBoard: {board['name']}\n"
            formatted_text += f"Lists: {board['lists_count']}, Cards: {board['cards_count']}\n"
            
            for lst in board['lists']:
                formatted_text += f"\n  List: {lst['title']}\n"
                for card in lst['cards']:
                    due_date = f" (Due: {card['due_date']})" if card['due_date'] else ""
                    formatted_text += f"    - {card['title']}{due_date}\n"
        
        return formatted_text or "No boards or cards available yet." 