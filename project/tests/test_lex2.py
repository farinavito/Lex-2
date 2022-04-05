from itertools import chain
import pytest
import brownie
from brownie import *
from brownie import accounts
from brownie.network import rpc
from brownie.network.state import Chain

#new agreement
commission = 1
signee = 1
receiver = 9
amount_sent = 10**1
agreement_duration = 2629743
initial_howLong = 30
agreements_number = 0


without_signee = [signee + 1, signee + 2, signee + 3]
without_receiver = [receiver - 1, receiver - 2, receiver - 3]


less_than_amount_sent = [amount_sent - 5, amount_sent - 6, amount_sent - 7]
more_than_amount_sent = [amount_sent + 10**2, amount_sent + 10**3, amount_sent + 10**4]


less_than_agreement_duration = [agreement_duration - 10**2, agreement_duration - 10**3, agreement_duration - 10**4]
more_than_agreement_duration = [agreement_duration + 10**5, agreement_duration + 10**6, agreement_duration + 10**7]

seconds_in_day = 60 * 60 * 24

protectorOwnerAddress = 1
protectorWaitingToBeOwnerAddress = 2
addressProtector1 = 3
addressProtector2 = 4
addressProtector3 = 5
addressProtector4 = 6
addressProtector5 = 7

@pytest.fixture()
def deploy_addressProtector(AddressProtector, module_isolation):
    return AddressProtector.deploy(accounts[protectorOwnerAddress], accounts[protectorWaitingToBeOwnerAddress], accounts[addressProtector1], accounts[addressProtector2], accounts[addressProtector3], accounts[addressProtector4], accounts[addressProtector5], {'from': accounts[0]})

@pytest.fixture()
def deploy(sendMoneyUntil, module_isolation):
    return sendMoneyUntil.deploy(deploy_addressProtector, {'from': accounts[0]})

@pytest.fixture(autouse=True)
def new_agreement(deploy, module_isolation):
    return deploy.createAgreement(accounts[receiver], amount_sent, agreement_duration, {'from': accounts[signee], 'value': amount_sent})
    

signee_2 = signee
receiver_2 = receiver
amount_sent_2 = 10**1
agreement_duration_2 = 31556926
initial_howLong_2 = 364
agreements_number_2 = 1

@pytest.fixture(autouse=True)
def new_agreement_2(deploy, module_isolation):
    return deploy.createAgreement(accounts[receiver_2], amount_sent_2, agreement_duration_2, {'from': accounts[signee_2], 'value': amount_sent_2})