# pylint: disable=C0114,C0115,C0116,C0117,W0719, R0903, E0402, C0301
# pylint: disable=attribute-defined-outside-init


from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from .domain_model import Authorizer, Notifier, Transaction, TransactionRepository, WalletRepository


@dataclass
class TransferMoney:
    wallet_repo: WalletRepository
    transaction_repo: TransactionRepository
    authorizer: Authorizer
    notifier: Notifier

    def execute(self, payer_user_id: int, payee_user_id: int, amount: Decimal) -> UUID:
        self._retrieve_wallets(payer_user_id, payee_user_id)
        self._transfer_money_and_create_transaction(amount)
        self._persist_wallets_and_transaction()
        self._send_notification()

        return self.transaction.id

    # ----------------------------
    # helpers methods
    # ----------------------------
    def _retrieve_wallets(self, payer_user_id, payee_user_id):
        if payer_user_id == payee_user_id:
            raise Exception("PayerMustDifferFromPayee")

        payee_wallet = self.wallet_repo.owned_by(payee_user_id)
        payer_wallet = self.wallet_repo.owned_by(payer_user_id)

        if payer_wallet is None:
            raise Exception("PayerWalletNotFound")

        if payee_wallet is None:
            raise Exception("PayeeWalletNotFound")

        self.payer_wallet = payer_wallet
        self.payee_wallet = payee_wallet

    def _transfer_money_and_create_transaction(self, amount):
        if not self.authorizer.is_payment_allowed():
            raise Exception("PaymentNotAllowed")

        self.payer_wallet.debit(amount)
        self.payee_wallet.credit(amount)
        self.transaction = Transaction(self.payer_wallet.id, self.payee_wallet.id, amount)

    def _persist_wallets_and_transaction(self):
        self.wallet_repo.update(self.payer_wallet)
        self.wallet_repo.update(self.payee_wallet)
        self.transaction_repo.save(self.transaction)

    def _send_notification(self):
        self.notifier.notify(self.transaction.id)
