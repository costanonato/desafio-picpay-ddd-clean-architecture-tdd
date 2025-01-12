# pylint: disable=C0114,C0115,C0116,C0117,W0719, R0903, E0402, C0301
# pylint: disable=attribute-defined-outside-init


from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from uuid import UUID, uuid4


class WalletType(Enum):
    COMMON = auto()
    MERCHANT = auto()


@dataclass
class Wallet:
    type: WalletType
    user_id: int
    balance: Decimal
    id: UUID = field(default_factory=uuid4)

    def credit(self, amount: Decimal):
        self.balance += amount

    def debit(self, amount: Decimal):
        if self.type is WalletType.MERCHANT:
            raise Exception("MerchantWalletCannotTransferMoney")

        if self.balance < amount:
            raise Exception("InsufficientBalance")

        self.balance -= amount


@dataclass
class Transaction:
    payer_wallet_id: UUID
    payee_wallet_id: UUID
    amount: Decimal
    processed_at: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)


class WalletRepository(ABC):
    @abstractmethod
    def owned_by(self, user_id: int) -> Wallet | None: ...

    @abstractmethod
    def update(self, wallet: Wallet): ...


class TransactionRepository(ABC):
    @abstractmethod
    def save(self, transaction: Transaction):
        pass


class Authorizer(ABC):
    @abstractmethod
    def is_payment_allowed(self) -> bool:
        pass


class Notifier(ABC):
    @abstractmethod
    def notify(self, transaction_id: UUID):
        pass
