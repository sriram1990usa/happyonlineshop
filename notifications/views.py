from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import Notification

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class MarkNotificationReadView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
            return JsonResponse({'success': True, 'message': 'Notification marked as read'})
        
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('notifications:list')
