from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("campaign", "0008_campaign_owner"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="steplog",
            new_name="step_camp_created_idx",
            old_name="campaign_st_campaign_4844ca_idx",
        ),
        migrations.RenameIndex(
            model_name="steplog",
            new_name="step_camp_type_action_idx",
            old_name="campaign_st_campaign_b4f13b_idx",
        ),
    ]
