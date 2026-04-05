from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("campaign", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="party",
            name="disease_risk_active",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="party",
            name="forced_departure",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="party",
            name="hardship_price_multiplier",
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="hero",
            name="days_unavailable",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="hero",
            name="has_pet_dog",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="hero",
            name="in_disguise",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="hero",
            name="investment_active",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="hero",
            name="is_waiting_outside",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="hero",
            name="temple_reroll_charges",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="SettlementLocationDef",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=40, unique=True)),
                ("name", models.CharField(max_length=120, unique=True)),
                ("always_available", models.BooleanField(default=False)),
                ("village_available", models.BooleanField(default=False)),
                ("town_find_target", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("city_find_target", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("definition", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
