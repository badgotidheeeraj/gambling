from bet_api.models.transaction import Transaction

class TransactionService:
    @staticmethod
    def create_transaction(user, amount, transaction_type, description=None):
        return Transaction.objects.create(
            user=user,
            amount=amount,
            transaction_type=transaction_type,
            description=description or ""
        )
