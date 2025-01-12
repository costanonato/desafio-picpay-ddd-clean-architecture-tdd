# pylint: disable=C0114,C0115,C0116,C0117,W0719, R0903, C0301
# pylint: disable=attribute-defined-outside-init


from uuid import UUID

from ..domain_model import Authorizer, Notifier, Transaction, TransactionRepository, Wallet, WalletRepository


class FakeWalletRepository(WalletRepository):
    def __init__(self):
        self.wallets = {}

    def owned_by(self, user_id: int) -> Wallet | None:
        return self.wallets.get(user_id)

    def update(self, wallet: Wallet):
        self.wallets[wallet.user_id] = wallet


class FakeTransactionRepository(TransactionRepository):
    def __init__(self):
        self.transactions = {}

    def save(self, transaction: Transaction):
        self.transactions[transaction.id] = transaction


class FakeAuthorizer(Authorizer):
    payment_allowed = True

    def is_payment_allowed(self) -> bool:
        return self.payment_allowed


class FakeNotifier(Notifier):
    def __init__(self):
        self.notifications = []

    def notify(self, transaction_id: UUID):
        self.notifications.append(transaction_id)
        self.notifications.append(transaction_id)
