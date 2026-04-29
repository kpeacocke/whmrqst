from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("campaign", "0002_campaign_state_and_locations"),
    ]

    operations = [
        migrations.CreateModel(
            name="HeroSkill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("source", models.CharField(default="training", max_length=60)),
                (
                    "hero",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hero_skills",
                        to="campaign.hero",
                    ),
                ),
                (
                    "skill_def",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="hero_skills",
                        to="campaign.skilldef",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "unique_together": {("hero", "skill_def")},
            },
        ),
    ]
