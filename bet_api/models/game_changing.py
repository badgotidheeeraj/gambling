from django.db import models
from django.contrib.auth.models import User

class CrashGameRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bet_amount = models.FloatField()
    multiplier_at_cashout = models.FloatField(null=True, blank=True)
    crash_point = models.FloatField()
    winnings = models.FloatField(default=0.0)
    cashed_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Bet: {self.bet_amount} - Won: {self.winnings}"