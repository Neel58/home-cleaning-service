from django.contrib.auth.models import User
from django.test import Client

client = Client()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin','admin@example.com','testpass123')
client.login(username='admin', password='testpass123')
res = client.get('/dashboard/analytics/')
print('status', res.status_code)
content = res.content.decode('utf-8')
idx = content.find('const months')
print('idx', idx)
if idx != -1:
    print(content[idx:idx+400])
idx2 = content.find('const revenue')
print('idx2', idx2)
if idx2 != -1:
    print(content[idx2:idx2+400])
print('is_dummy_data:', res.context.get('is_dummy_data', None))
