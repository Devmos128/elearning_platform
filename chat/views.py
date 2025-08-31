from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ChatRoom, Message


@login_required
def chat_room(request, room_name):
    # Get existing room or create new one
    try:
        room = ChatRoom.objects.get(name=room_name)
    except ChatRoom.DoesNotExist:
        # Create new room with created_by field
        room = ChatRoom.objects.create(name=room_name, created_by=request.user)
    
    # Add user to participants if not already
    if request.user not in room.participants.all():
        room.participants.add(request.user)
    
    chat_messages = Message.objects.filter(room=room).order_by('timestamp')
    
    context = {
        'room_name': room_name,
        'messages': chat_messages,
        'participants': room.participants.all(),
    }
    return render(request, 'chat/room.html', context)


@login_required
def chat_list(request):
    # rooms = ChatRoom.objects.filter(participants=request.user)
    rooms = ChatRoom.objects.all().order_by('-created_at')
    context = {
        'rooms': rooms,
    }
    return render(request, 'chat/chat_list.html', context)


@login_required
def create_chat_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        if room_name:
            # Check if room already exists
            try:
                room = ChatRoom.objects.get(name=room_name)
            except ChatRoom.DoesNotExist:
                # Create new room with created_by field
                room = ChatRoom.objects.create(name=room_name, created_by=request.user)
            
            # Add user to participants if not already
            if request.user not in room.participants.all():
                room.participants.add(request.user)
            
            return redirect('chat_room', room_name=room_name)
    
    return render(request, 'chat/create_room.html')


@login_required
def delete_chat_room(request, room_name):
    """Delete a chat room (only by the creator)"""
    try:
        room = ChatRoom.objects.get(name=room_name, created_by=request.user)
        room_title = room.name
        
        # Get all participants for notifications
        participants = room.participants.all()
        
        # Create notifications for all participants
        from users.models import Notification
        for participant in participants:
            if participant != request.user:  # Don't notify the creator
                Notification.objects.create(
                    user=participant,
                    notification_type='removed',
                    title='Chat Room Deleted',
                    message=f'The chat room "{room_title}" has been deleted by {request.user.get_full_name() or request.user.username}.',
                    related_user=request.user
                )
        
        # Delete the room
        room.delete()
        messages.success(request, f'Chat room "{room_title}" has been deleted successfully.')
        
    except ChatRoom.DoesNotExist:
        messages.error(request, 'Chat room not found or you do not have permission to delete it.')
    
    return redirect('chat_list')
