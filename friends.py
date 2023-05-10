from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import FriendRequest, Friendship

@login_required
def send_friend_request(request, user_id): #отправка заявки в друзья
    to_user = get_object_or_404(User, id=user_id)
    from_user = request.user
    # Проверяем, что заявка в друзья не была отправлена ранее
    if not FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
        # Создаем заявку в друзья
        friend_request = FriendRequest(from_user=from_user, to_user=to_user)
        friend_request.save()
    return redirect('home')




@login_required 
def accept_friend_request(request, request_id): # принятиe/отклонениe заявки в друзья
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    # Проверяем, что заявка принадлежит текущему пользователю
    if friend_request.to_user == request.user:
        friend_request.accepted = True
        friend_request.save()
        # Если у обоих пользователей уже есть заявки в друзья друг к другу, то создаем дружбу
        if FriendRequest.objects.filter(from_user=friend_request.to_user, to_user=friend_request.from_user, accepted=True).exists():
            friendship = Friendship(user1=friend_request.from_user, user2=friend_request.to_user)
            friendship.save()
    return redirect('home')

@login_required
def reject_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    # Проверяем, что заявка принадлежит текущему пользователю
    if friend_request.to_user == request.user:
        friend_request.delete()
    return redirect('home')

@login_required
def friend_requests(request):
    friend_requests_received = FriendRequest.objects.filter(to_user=request.user, accepted=False)
    friend_requests_sent = FriendRequest.objects.filter(from_user=request.user, accepted=False)
    return render(request, 'friends/friend_requests.html', {'friend_requests_received': friend_requests_received, 'friend_requests_sent': friend_requests_sent})


@login_required
def friends(request):
    friendships_as_user1 = Friendship.objects.filter(user1=request.user)
    friendships_as_user2 = Friendship.objects.filter(user2=request.user)
    friends = []
    for friendship in friendships_as_user1:
        friends.append(friendship.user2)
    for friendship in friendships_as_user2:
        friends.append(friendship.user1)
    return render(request, 'friends/friends.html', {'friends': friends})

@login_required
def friendship_status(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    # Если пользователи уже друзья
    if Friendship.objects.filter(user1=request.user, user2=other_user).exists() or Friendship.objects.filter(user1=other_user, user2=request.user).exists():
        return 'Друзья'
    # Если пользователь отправил заявку в друзья
    elif FriendRequest.objects.filter(from_user=request.user, to_user=other_user, accepted=False).exists():
        return 'Отправлена заявка в друзья'
    # Если пользователь получил заявку в друзья
    elif FriendRequest.objects.filter(from_user=other_user, to_user=request.user, accepted=False).exists():
        return 'Получена заявка в друзья'
    # Если пользователи не являются друзьями и заявки в друзья не было
    else:
        return 'Нет отношений'
    

@login_required
def remove_friend(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    # Удаляем дружбу, если она существует
    if Friendship.objects.filter(user1=request.user, user2=other_user).exists() or Friendship.objects.filter(user1=other_user, user2=request.user).exists():
        Friendship.objects.filter(user1=request.user, user2=other_user).delete()
        Friendship.objects.filter(user1=other_user, user2=request.user).delete()
    return redirect('home')
