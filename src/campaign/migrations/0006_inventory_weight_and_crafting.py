from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("campaign", "0005_hero_alive_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="itemdef",
            name="weight",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="CraftingRecipeDef",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=40, unique=True)),
                ("name", models.CharField(max_length=120, unique=True)),
                ("definition", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
