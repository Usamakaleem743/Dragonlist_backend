from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from .models import Board, List, Card, Label, Checklist, ChecklistItem, Attachment, CardLocation, CardMember, CardDate, Comment
from .serializers import (
    BoardSerializer, ListSerializer, CardSerializer, LabelSerializer, 
    ChecklistSerializer, ChecklistItemSerializer, AttachmentSerializer, 
    CardLocationSerializer, RegisterSerializer, LoginSerializer, UserSerializer,
    CardMemberSerializer, CardDateSerializer, CommentSerializer
)
from .permissions import IsBoardMember, IsListBoardMember, IsCardBoardMember
from .utils import get_next_order, reorder_items
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from .services.ai_service import AIService
import asyncio

User = get_user_model()

# Create your views here.

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # Add this line to disable authentication for login

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    refresh = RefreshToken.for_user(user)
                    print(f"Login successful for user: {email}")  # Debug log
                    return Response({
                        'user': UserSerializer(user).data,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }, status=status.HTTP_200_OK)
                else:
                    print(f"Invalid password for user: {email}")
            except User.DoesNotExist:
                print(f"User not found with email: {email}")
            
            return Response(
                {'error': 'Invalid email or password'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        print(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListViewSet(viewsets.ModelViewSet):
    serializer_class = ListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return lists created by the current user
        return List.objects.filter(user=self.request.user).order_by('order')

    def perform_create(self, serializer):
        # Set the current user when creating a new list
        order = get_next_order(List.objects.filter(user=self.request.user))
        serializer.save(user=self.request.user, order=order)

    def perform_update(self, serializer):
        try:
            if 'order' in self.request.data:
                # Only reorder lists belonging to the current user
                other_lists = List.objects.filter(
                    user=self.request.user
                ).exclude(id=self.get_object().id)
                new_order = float(self.request.data['order'])
                
                for list_obj in other_lists:
                    if list_obj.order >= new_order:
                        list_obj.order = list_obj.order + 1
                        list_obj.save()
                
                serializer.save(order=new_order)
            else:
                serializer.save()
        except Exception as e:
            print(f"Error in perform_update: {str(e)}")
            raise e

class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return cards created by the current user
        return Card.objects.filter(user=self.request.user).select_related('list')

    def perform_create(self, serializer):
        list_obj = serializer.validated_data['list']
        
        # Ensure the list belongs to the current user
        if list_obj.user != self.request.user:
            raise PermissionDenied("You can only create cards in your own lists")
            
        order = get_next_order(Card.objects.filter(
            list=list_obj,
            user=self.request.user
        ))
        serializer.save(user=self.request.user, order=order)

    def perform_update(self, serializer):
        if 'order' in self.request.data:
            list_obj = self.get_object().list
            reorder_items(Card.objects.filter(list=list_obj), 
                         self.get_object().id, 
                         int(self.request.data['order']))
        else:
            serializer.save()

    @action(detail=True, methods=['GET'])
    def members(self, request, pk=None):
        """Get all members of a card"""
        card = self.get_object()
        serializer = UserSerializer(card.members.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def add_member(self, request, pk=None):
        """Add a member to the card"""
        card = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            # Check if user is a member of the board
            if user not in card.list.board.members.all():
                return Response(
                    {'error': 'User must be a board member first'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user is already assigned to the card
            if user in card.members.all():
                return Response(
                    {'error': 'User is already assigned to this card'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            card.members.add(user)
            return Response(CardSerializer(card).data)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['DELETE'])
    def remove_member(self, request, pk=None):
        """Remove a member from the card"""
        card = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            if user not in card.members.all():
                return Response(
                    {'error': 'User is not assigned to this card'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            card.members.remove(user)
            return Response(CardSerializer(card).data)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['POST'])
    def assign_multiple_members(self, request, pk=None):
        """Assign multiple members to a card at once"""
        card = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        if not isinstance(user_ids, list):
            return Response(
                {'error': 'user_ids must be a list'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        added_users = []
        errors = []
        
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                if user in card.list.board.members.all():
                    if user not in card.members.all():
                        card.members.add(user)
                        added_users.append(user_id)
                    else:
                        errors.append(f"User {user_id} is already assigned to this card")
                else:
                    errors.append(f"User {user_id} is not a board member")
            except User.DoesNotExist:
                errors.append(f"User {user_id} not found")
        
        return Response({
            'card': CardSerializer(card).data,
            'added_users': added_users,
            'errors': errors
        })

    @action(detail=True, methods=['POST'])
    def labels(self, request, pk=None):
        card = self.get_object()
        # Create new label directly with card reference
        label_data = {
            'title': request.data.get('title'),
            'color': request.data.get('color'),
            'card': card.id
        }
        serializer = LabelSerializer(data=label_data)
        if serializer.is_valid():
            serializer.save()
            return Response(CardSerializer(card).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='labels/(?P<label_pk>[^/.]+)')
    def remove_label(self, request, pk=None, label_pk=None):
        try:
            card = self.get_object()
            # Simply delete the label since it's directly linked to the card
            Label.objects.filter(pk=label_pk, card=card).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"Error removing label: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['POST'])
    def optimize_description(self, request, pk=None):
        try:
            card = self.get_object()
            prompt = request.data.get('description', '')
            
            # Create AI service instance
            ai_service = AIService()
            
            # Get optimized description
            optimized_description = asyncio.run(
                ai_service.optimize_description(prompt)
            )
            
            # Update card description
            card.description = optimized_description
            card.save()
            
            return Response({
                'description': optimized_description
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Label.objects.all()

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Only update specific fields that are provided
            if 'title' in request.data:
                instance.title = request.data['title']
            if 'color' in request.data:
                instance.color = request.data['color']
            
            # Save only the changed fields
            instance.save(update_fields=['title', 'color'] if 'color' in request.data else ['title'])
            
            # Return the full serialized instance
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
            
        except Label.DoesNotExist:
            return Response(
                {'error': 'Label not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        # If card_id is provided, get the card instance
        card_id = self.request.data.get('card')
        if card_id:
            try:
                card = Card.objects.get(pk=card_id)
                serializer.save(card=card)
            except Card.DoesNotExist:
                raise ValidationError('Invalid card ID')
        else:
            serializer.save()

class ChecklistViewSet(viewsets.ModelViewSet):
    queryset = Checklist.objects.all()
    serializer_class = ChecklistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Checklist.objects.filter(
            card__list__board__members=self.request.user
        )

    def perform_create(self, serializer):
        card = get_object_or_404(Card, pk=self.request.data.get('card'))
        serializer.save(card=card)

    def destroy(self, request, *args, **kwargs):
        try:
            checklist = self.get_object()  # This gets a single Checklist instance
            print(f"Found checklist: {checklist.id}")
            
            if checklist.card.list.board.members.filter(id=request.user.id).exists():
                # Get all items for this specific checklist
                items = ChecklistItem.objects.filter(checklist=checklist)
                print(f"Found {items.count()} items to delete")
                
                # Delete the items
                items.delete()
                print("Deleted items")
                
                # Delete the checklist
                checklist.delete()
                print("Deleted checklist")
                
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'error': "You don't have permission to delete this checklist"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Exception as e:
            print(f"Error during deletion: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ChecklistItemViewSet(viewsets.ModelViewSet):
    serializer_class = ChecklistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChecklistItem.objects.filter(
            checklist__card__list__board__members=self.request.user
        )

    def perform_create(self, serializer):
        checklist = get_object_or_404(Checklist, pk=self.request.data.get('checklist'))
        order = get_next_order(ChecklistItem.objects.filter(checklist=checklist))
        serializer.save(checklist=checklist, order=order)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'is_completed' in request.data:
            instance.is_completed = request.data['is_completed']
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['PATCH'])
    def toggle(self, request, pk=None):
        try:
            print(f"Attempting to toggle item {pk}")  # Debug log
            
            # Get the item directly
            item = ChecklistItem.objects.get(pk=pk)
            print(f"Found item: {item}")  # Debug log
            
            # Toggle the status
            item.is_completed = not item.is_completed
            item.save()
            
            print(f"Toggled status to: {item.is_completed}")  # Debug log
            
            # Return the updated item
            return Response({
                'id': item.id,
                'is_completed': item.is_completed,
                'title': item.title
            })
            
        except ChecklistItem.DoesNotExist:
            print(f"Item {pk} not found")  # Debug log
            return Response(
                {'error': f'Item {pk} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error: {str(e)}")  # Debug log
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class AttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCardBoardMember]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return Attachment.objects.filter(
            card__list__board__members=self.request.user
        )

    def perform_create(self, serializer):
        card = get_object_or_404(Card, pk=self.request.data.get('card'))
        serializer.save(card=card)

class CardLocationViewSet(viewsets.ModelViewSet):
    serializer_class = CardLocationSerializer
    permission_classes = [permissions.IsAuthenticated, IsCardBoardMember]

    def get_queryset(self):
        return CardLocation.objects.filter(
            card__list__board__members=self.request.user
        )

    def perform_create(self, serializer):
        card = get_object_or_404(Card, pk=self.request.data.get('card'))
        serializer.save(card=card)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def all_users(self, request):
        """Get all users in the system"""
        users = User.objects.all()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_card_member(request, card_pk):
    try:
        card = Card.objects.get(pk=card_pk)
        user = User.objects.get(pk=request.data.get('user_id'))
        
        member, created = CardMember.objects.get_or_create(
            card=card,
            user=user
        )
        
        serializer = CardMemberSerializer(member)
        return Response(serializer.data)
    except Card.DoesNotExist:
        return Response({'error': 'Card not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_card_member(request, card_pk):
    try:
        user_id = request.data.get('user_id')  # Get user_id from request body
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        member = CardMember.objects.filter(
            card_id=card_pk,
            user_id=user_id
        ).first()

        if member:
            member.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'error': 'Member not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_card_dates(request, card_pk):
    try:
        card = Card.objects.get(pk=card_pk)
        print("Received dates data:", request.data)  # Debug print
        
        card_date, created = CardDate.objects.get_or_create(card=card)
        
        # Update fields
        card_date.start_date = request.data.get('start_date')
        card_date.due_date = request.data.get('due_date')
        card_date.is_complete = request.data.get('is_complete', False)
        card_date.save()
        
        serializer = CardDateSerializer(card_date)
        return Response(serializer.data)
    except Card.DoesNotExist:
        return Response(
            {'error': 'Card not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print("Error:", str(e))  # Debug print
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_card_dates(request, card_pk):
    try:
        card = Card.objects.get(pk=card_pk)
        card_date = CardDate.objects.filter(card=card).first()
        
        if card_date:
            card_date.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Dates not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Card.DoesNotExist:
        return Response(
            {'error': 'Card not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(
            card__list__board__members=self.request.user
        )

    def perform_create(self, serializer):
        card_id = self.kwargs.get('card_pk')
        card = get_object_or_404(Card, pk=card_id)
        serializer.save(author=self.request.user, card=card)

    @action(detail=True, methods=['PATCH'])
    def update_content(self, request, pk=None):
        comment = self.get_object()
        if comment.author != request.user:
            return Response(
                {'error': 'You can only edit your own comments'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        comment.content = request.data.get('content')
        comment.save()
        serializer = self.get_serializer(comment)
        return Response(serializer.data)

# Additional ViewSets for other models...
