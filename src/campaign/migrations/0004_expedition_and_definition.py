from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("campaign", "0003_hero_skill"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExpeditionDef",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=40, unique=True)),
                ("name", models.CharField(max_length=120, unique=True)),
                ("base_reward_min", models.PositiveIntegerField(default=25)),
                ("base_reward_max", models.PositiveIntegerField(default=120)),
                ("base_supply_cost", models.PositiveSmallIntegerField(default=1)),
                ("base_injury_risk", models.PositiveSmallIntegerField(default=2)),
                ("difficulty", models.PositiveSmallIntegerField(default=1)),
                ("definition", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Expedition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "risk_level",
                    models.CharField(
                        choices=[("cautious", "Cautious"), ("standard", "Standard"), ("reckless", "Reckless")],
                        default="standard",
                        max_length=20,
                    ),
                ),
                ("result", models.JSONField(blank=True, default=dict)),
                (
                    "campaign",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="expeditions",
                        to="campaign.campaign",
                    ),
                ),
                (
                    "expedition_def",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="expeditions",
                        to="campaign.expeditiondef",
                    ),
                ),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="expeditions",
                        to="campaign.party",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
