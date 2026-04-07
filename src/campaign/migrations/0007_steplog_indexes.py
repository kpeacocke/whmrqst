from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("campaign", "0006_inventory_weight_and_crafting"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="steplog",
            index=models.Index(fields=["campaign", "created_at"], name="campaign_st_campaign_4844ca_idx"),
        ),
        migrations.AddIndex(
            model_name="steplog",
            index=models.Index(
                fields=["campaign", "step_type", "action_type"],
                name="campaign_st_campaign_b4f13b_idx",
            ),
        ),
    ]
