from django.db import migrations, models


def dedupe_predictions_per_match(apps, schema_editor):
    Prediction = apps.get_model("predictions", "Prediction")
    seen = {}
    to_delete = []
    for pred in Prediction.objects.order_by("user_id", "match_id", "-updated_at"):
        key = (pred.user_id, pred.match_id)
        if key in seen:
            to_delete.append(pred.id)
        else:
            seen[key] = pred.id
    if to_delete:
        Prediction.objects.filter(id__in=to_delete).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("predictions", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="prediction",
            unique_together=set(),
        ),
        migrations.RunPython(dedupe_predictions_per_match, migrations.RunPython.noop),
        migrations.RemoveIndex(
            model_name="prediction",
            name="predictions_user_id_e189bb_idx",
        ),
        migrations.RemoveIndex(
            model_name="prediction",
            name="predictions_group_i_a71f79_idx",
        ),
        migrations.RemoveIndex(
            model_name="prediction",
            name="predictions_group_i_e3f9a5_idx",
        ),
        migrations.RemoveField(
            model_name="prediction",
            name="group",
        ),
        migrations.AlterUniqueTogether(
            name="prediction",
            unique_together={("user", "match")},
        ),
        migrations.AddIndex(
            model_name="prediction",
            index=models.Index(fields=["user", "match"], name="predictions_user_id_match_idx"),
        ),
    ]
