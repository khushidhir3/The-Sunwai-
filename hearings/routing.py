"""WebSocket URL routing for hearings."""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/hearing/(?P<hearing_id>\d+)/chat/$', consumers.HearingChatConsumer.as_asgi()),
]
