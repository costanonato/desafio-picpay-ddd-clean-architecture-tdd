# pylint: disable=C0114,C0115,C0116,C0117,W0719, R0903, E0402, C0301
# pylint: disable=attribute-defined-outside-init


from decimal import Decimal

import pytest

from .scenario import TransferMoneyTestScenario

# -----------------------

PAYER_USER_ID = 111
PAYEE_USER_ID = 222
INVALID_USER_ID = 999
AMOUNT_100 = Decimal(100)
AMOUNT_150 = Decimal(150)
AMOUNT_50 = Decimal(50)
AMOUNT_0 = Decimal(0)


# -----------------------
# BUSINESS
# -----------------------


def test_transfer_succeeds_from_common_wallet():
    # given
    test_scenario = TransferMoneyTestScenario()
    test_scenario.create_common_wallet(PAYER_USER_ID, AMOUNT_100)
    test_scenario.create_merchant_wallet(PAYEE_USER_ID, AMOUNT_100)
    test_scenario.payment_allowed_by_authorizer(True)

    # when
    transaction_id = test_scenario.execute_usecase(PAYER_USER_ID, PAYEE_USER_ID, AMOUNT_50)

    # then
    assert test_scenario.transaction_was_created(transaction_id)
    assert test_scenario.notification_was_sent(transaction_id)
    assert test_scenario.wallet_balance_of(PAYER_USER_ID) == AMOUNT_50
    assert test_scenario.wallet_balance_of(PAYEE_USER_ID) == AMOUNT_150


def test_transfer_succeeds_if_balance_equals_transfer_amount():
    # given
    test_scenario = TransferMoneyTestScenario()
    test_scenario.create_common_wallet(PAYER_USER_ID, AMOUNT_50)
    test_scenario.create_merchant_wallet(PAYEE_USER_ID, AMOUNT_50)
    test_scenario.payment_allowed_by_authorizer(True)

    # when
    transaction_id = test_scenario.execute_usecase(PAYER_USER_ID, PAYEE_USER_ID, AMOUNT_50)

    # then
    assert test_scenario.transaction_was_created(transaction_id)
    assert test_scenario.notification_was_sent(transaction_id)
    assert test_scenario.wallet_balance_of(PAYER_USER_ID) == AMOUNT_0
    assert test_scenario.wallet_balance_of(PAYEE_USER_ID) == AMOUNT_100


def test_transfer_fails_from_merchant_wallet():
    # given
    test_scenario = TransferMoneyTestScenario()
    test_scenario.create_merchant_wallet(PAYER_USER_ID, AMOUNT_50)
    test_scenario.create_merchant_wallet(PAYEE_USER_ID, AMOUNT_50)
    test_scenario.payment_allowed_by_authorizer(True)

    # when / then
    with pytest.raises(Exception, match="MerchantWalletCannotTransferMoney"):
        test_scenario.execute_usecase(PAYER_USER_ID, PAYEE_USER_ID, AMOUNT_50)

    # then
    assert test_scenario.no_transaction_was_created()
    assert test_scenario.no_notification_was_sent()
    assert test_scenario.wallet_balance_of(PAYER_USER_ID) == AMOUNT_50
    assert test_scenario.wallet_balance_of(PAYEE_USER_ID) == AMOUNT_50


def test_transfer_fails_from_wallet_with_insufficient_balance():
    # given
    test_scenario = TransferMoneyTestScenario()
    test_scenario.create_common_wallet(PAYER_USER_ID, AMOUNT_50)
    test_scenario.create_merchant_wallet(PAYEE_USER_ID, AMOUNT_50)
    test_scenario.payment_allowed_by_authorizer(True)

    # when / then
    with pytest.raises(Exception, match="InsufficientBalance"):
        test_scenario.execute_usecase(PAYER_USER_ID, PAYEE_USER_ID, AMOUNT_100)

    # then
    assert test_scenario.no_transaction_was_created()
    assert test_scenario.no_notification_was_sent()
    assert test_scenario.wallet_balance_of(PAYER_USER_ID) == AMOUNT_50
    assert test_scenario.wallet_balance_of(PAYEE_USER_ID) == AMOUNT_50


def test_transfer_fails_if_not_allowed_by_authorizer():
    # given
    test_scenario = TransferMoneyTestScenario()
    test_scenario.create_common_wallet(PAYER_USER_ID, AMOUNT_50)
    test_scenario.create_merchant_wallet(PAYEE_USER_ID, AMOUNT_50)
    test_scenario.payment_allowed_by_authorizer(False)

    # when / then
    with pytest.raises(Exception, match="PaymentNotAllowed"):
        test_scenario.execute_usecase(PAYER_USER_ID, PAYEE_USER_ID, AMOUNT_100)

    # then
    assert test_scenario.no_transaction_was_created()
    assert test_scenario.no_notification_was_sent()
    assert test_scenario.wallet_balance_of(PAYER_USER_ID) == AMOUNT_50
    assert test_scenario.wallet_balance_of(PAYEE_USER_ID) == AMOUNT_50


# -----------------------
# TECHNICAL
# -----------------------


def test_transfer_fails_with_invalid_payer_user_id():
    # given
    test_scenario = TransferMoneyTestScenario()
    test_scenario.create_common_wallet(PAYER_USER_ID, AMOUNT_50)
    test_scenario.create_merchant_wallet(PAYEE_USER_ID, AMOUNT_50)
    test_scenario.payment_allowed_by_authorizer(False)

    # when / then
    with pytest.raises(Exception, match="PayerWalletNotFound"):
        test_scenario.execute_usecase(INVALID_USER_ID, PAYEE_USER_ID, AMOUNT_100)

    # then
    assert test_scenario.no_transaction_was_created()
    assert test_scenario.no_notification_was_sent()
    assert test_scenario.wallet_balance_of(PAYER_USER_ID) == AMOUNT_50
    assert test_scenario.wallet_balance_of(PAYEE_USER_ID) == AMOUNT_50


def test_transfer_fails_with_invalid_payee_user_id():
    # given
    test_scenario = TransferMoneyTestScenario()
    test_scenario.create_common_wallet(PAYER_USER_ID, AMOUNT_50)
    test_scenario.create_merchant_wallet(PAYEE_USER_ID, AMOUNT_50)
    test_scenario.payment_allowed_by_authorizer(False)

    # when / then
    with pytest.raises(Exception, match="PayeeWalletNotFound"):
        test_scenario.execute_usecase(PAYEE_USER_ID, INVALID_USER_ID, AMOUNT_100)

    # then
    assert test_scenario.no_transaction_was_created()
    assert test_scenario.no_notification_was_sent()
    assert test_scenario.wallet_balance_of(PAYER_USER_ID) == AMOUNT_50
    assert test_scenario.wallet_balance_of(PAYEE_USER_ID) == AMOUNT_50


def test_transfer_fails_if_payer_and_payee_are_same():
    # given
    test_scenario = TransferMoneyTestScenario()
    test_scenario.create_common_wallet(PAYER_USER_ID, AMOUNT_50)
    test_scenario.payment_allowed_by_authorizer(False)

    # when / then
    with pytest.raises(Exception, match="PayerMustDifferFromPayee"):
        test_scenario.execute_usecase(PAYER_USER_ID, PAYER_USER_ID, AMOUNT_100)

    # then
    assert test_scenario.no_transaction_was_created()
    assert test_scenario.no_notification_was_sent()
    assert test_scenario.wallet_balance_of(PAYER_USER_ID) == AMOUNT_50
