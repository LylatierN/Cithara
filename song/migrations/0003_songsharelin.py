import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('song', '0002_alter_prompt_lyrics'),
    ]

    operations = [
        migrations.CreateModel(
            name='SongShareLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(
                    default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('song', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='share_link',
                    to='song.song',
                )),
            ],
        ),
    ]
