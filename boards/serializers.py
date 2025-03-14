from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Board, List, Card, Label, Checklist, ChecklistItem, Attachment, CardLocation, CardMember, CardDate, Comment

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class CardLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardLocation
        fields = ('id', 'latitude', 'longitude', 'place_name')

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('id', 'title', 'file', 'url', 'created_at')

class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ['id', 'title', 'is_completed', 'checklist', 'order', 'created_at']

class ChecklistSerializer(serializers.ModelSerializer):
    items = ChecklistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Checklist
        fields = ('id', 'title', 'items', 'card', 'created_at')

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['id', 'title', 'color', 'card', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'card': {'required': False},  # Make card field optional
            'color': {'required': False}  # Make color field optional
        }

    def update(self, instance, validated_data):
        # Only update the fields that are provided
        if 'title' in validated_data:
            instance.title = validated_data['title']
        if 'color' in validated_data:
            instance.color = validated_data['color']
        instance.save()
        return instance

class CardMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = CardMember
        fields = ['id', 'card', 'user', 'created_at']
        read_only_fields = ['created_at']

class CardDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardDate
        fields = ['id', 'start_date', 'due_date', 'is_complete']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at', 'updated_at']
        read_only_fields = ['author']

class CardSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, read_only=True)
    members = serializers.SerializerMethodField()
    dates = CardDateSerializer(source='card_date', read_only=True)
    checklist_items = ChecklistItemSerializer(many=True, read_only=True)
    checklists = ChecklistSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    location = CardLocationSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Card
        fields = [
            'id', 
            'title', 
            'description', 
            'list', 
            'user',
            'order',
            'labels',
            'members',
            'dates',
            'checklist_items',
            'checklists',
            'location',
            'attachments',
            'comments',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']

    def get_labels(self, obj):
        return [{'id': label.id, 'title': label.title, 'color': label.color} for label in obj.labels.all()]

    def get_members(self, obj):
        card_members = CardMember.objects.filter(card=obj)
        return [
            {
                'id': member.user.id,
                'username': member.user.username,
                'email': member.user.email,
                'first_name': member.user.first_name,
                'last_name': member.user.last_name,
            } 
            for member in card_members
        ]

class ListSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)

    class Meta:
        model = List
        fields = ['id', 'title', 'order', 'user', 'created_at', 'updated_at', 'cards']
        read_only_fields = ['created_at', 'updated_at', 'user']

class BoardSerializer(serializers.ModelSerializer):
    lists = ListSerializer(many=True, read_only=True)
    members = UserSerializer(many=True, read_only=True)
    labels = LabelSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Board
        fields = ('id', 'title', 'background', 'owner', 'members',
                 'lists', 'labels', 'created_at', 'updated_at')

# Authentication Serializers
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def create(self, validated_data):
        # Create username from email
        username = validated_data['email'].split('@')[0]
        base_username = username
        counter = 1
        
        # Ensure unique username
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
            
        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            raise serializers.ValidationError("Both email and password are required.")
        
        return data

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at', 'updated_at']
        read_only_fields = ['author'] 