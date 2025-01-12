# pylint: disable=C0114,C0115,C0116,C0117,W0719, C0301
# pylint: disable=attribute-defined-outside-init

from ..domain_model import Wallet, WalletType
from ..usecases import TransferMoney
from .fakers import FakeAuthorizer, FakeNotifier, FakeTransactionRepository, FakeWalletRepository


class TransferMoneyTestScenario:
    def __init__(self):
        self.wallet_repo = FakeWalletRepository()
        self.transaction_repo = FakeTransactionRepository()
        self.authorizer = FakeAuthorizer()
        self.notifier = FakeNotifier()
        self.usecase = TransferMoney(self.wallet_repo, self.transaction_repo, self.authorizer, self.notifier)

    # GIVEN
    def create_common_wallet(self, user_id, balance):
        wallet = Wallet(WalletType.COMMON, user_id, balance)
        self.wallet_repo.wallets[user_id] = wallet

    def create_merchant_wallet(self, user_id, balance):
        wallet = Wallet(WalletType.MERCHANT, user_id, balance)
        self.wallet_repo.wallets[user_id] = wallet

    def payment_allowed_by_authorizer(self, payment_allowed):
        self.authorizer.payment_allowed = payment_allowed

    # WHEN
    def execute_usecase(self, payer_user_id, payee_user_id, amount):
        return self.usecase.execute(payer_user_id, payee_user_id, amount)

    # THEN
    def wallet_balance_of(self, user_id):
        return self.wallet_repo.wallets[user_id].balance

    def transaction_was_created(self, transaction_id):
        return transaction_id in self.transaction_repo.transactions and len(self.transaction_repo.transactions) == 1

    def no_transaction_was_created(self):
        return len(self.transaction_repo.transactions) == 0

    def notification_was_sent(self, transaction_id):
        return transaction_id in self.transaction_repo.transactions

    def no_notification_was_sent(self):
        return len(self.notifier.notifications) == 0
