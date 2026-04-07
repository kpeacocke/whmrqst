from django.urls import path

from campaign import views

app_name = "campaign"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("campaign/<int:campaign_id>/", views.campaign_detail, name="campaign_detail"),
    path("campaign/<int:campaign_id>/expedition/", views.resolve_expedition_run, name="resolve_expedition_run"),
    path("campaign/<int:campaign_id>/travel/", views.resolve_travel, name="resolve_travel"),
    path("campaign/<int:campaign_id>/action/", views.resolve_hero_action, name="resolve_hero_action"),
    path("campaign/<int:campaign_id>/shop/", views.resolve_shop_transaction, name="resolve_shop_transaction"),
    path("campaign/<int:campaign_id>/craft/", views.resolve_crafting_action, name="resolve_crafting_action"),
    path("gm/", views.gm_console, name="gm_console"),
    path("gm/seed/", views.seed_warhammer_content, name="seed_warhammer_content"),
    path("step/<int:step_id>/", views.step_log_detail, name="step_log_detail"),
]
