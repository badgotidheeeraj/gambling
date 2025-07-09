from django.contrib import admin
from bet_api.models import UserProfile, ChatMessage, Notification, CrashGameRecord, Transaction


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "userAccount",
        "phone_number",
        "balance",
        "is_verified",
        "address",
        "date_of_birth",
        "profile_picture",
    )


@admin.register(ChatMessage)
class Chatting(admin.ModelAdmin):
    list_display = ("sender", "receiver", "message", "timestamp")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "is_read", "created_at")


@admin.register(CrashGameRecord)
class CrashGameRecordAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "bet_amount",
        "multiplier_at_cashout",
        "crash_point",
        "winnings",
        "cashed_out",
        "created_at",
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "transaction_type", "description", "created_at")
