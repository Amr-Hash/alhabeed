import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0002_cupgroup_matchday"),
    ]

    operations = [
        migrations.AddField(
            model_name="tournament",
            name="is_active",
            field=models.BooleanField(
                default=True,
                help_text="Inactive tournaments are hidden from users (still manageable in admin).",
            ),
        ),
        migrations.AddIndex(
            model_name="tournament",
            index=models.Index(fields=["is_active"], name="tournaments_is_acti_idx"),
        ),
    ]
