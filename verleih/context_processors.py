from .models import Group

def groups_processor(request):
    if request.user.is_authenticated:
        groups = Group.objects.filter(members=request.user)
    else:
        groups = []

    return {'groups': groups}