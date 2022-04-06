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
amount_sent = 10**10
deposit = 100
agreement_duration = 2629743 + 1649185494
initial_howLong = 30
agreements_number = 1


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
'''
@pytest.fixture()
def deploy(sendMoneyUntil, deploy_addressProtector, module_isolation):
    return sendMoneyUntil.deploy(deploy_addressProtector, {'from': accounts[0]})
'''
@pytest.fixture()
def deploy(sendMoneyUntil, module_isolation):
    return sendMoneyUntil.deploy({'from': accounts[0]})

@pytest.fixture(autouse=True)
def new_agreement(deploy, module_isolation):
    return deploy.createAgreement(accounts[receiver], amount_sent, agreement_duration, {'from': accounts[signee], 'value': deposit})
    
'''
signee_2 = signee
receiver_2 = receiver
amount_sent_2 = 10**1
agreement_duration_2 = 31556926 + 1649185494
initial_howLong_2 = 364
agreements_number_2 = 1

@pytest.fixture(autouse=True)
def new_agreement_2(deploy, module_isolation):
    return deploy.createAgreement(accounts[receiver_2], amount_sent_2, agreement_duration_2, {'from': accounts[signee_2], 'value': amount_sent_2})
'''


'''TESTING CREATEAGREEMENT AGREEMENT 1'''


@pytest.mark.aaa
def test_exactAgreement_id(deploy):
    '''check if the first id of the agreement is zero'''
    assert deploy.exactAgreement(agreements_number)[0] == str(agreements_number)
@pytest.mark.aaa
def test_exactAgreement_signee(deploy):
    '''check if the first address of the agreement's signee is the same as the signee'''
    assert deploy.exactAgreement(agreements_number)[1] == accounts[signee]
@pytest.mark.aaa
def test_exactAgreement_receiver(deploy):
    '''check if the first address of the agreement's receiver is the same as the accounts[0]'''
    assert deploy.exactAgreement(agreements_number)[2] == accounts[receiver]
@pytest.mark.aaa
def test_exactAgreement_amount(deploy):
    '''check if the amount of the agreement is 2'''
    assert deploy.exactAgreement(agreements_number)[3] == amount_sent  
@pytest.mark.aaa
def test_exactAgreement_deposit(deploy):
    '''check if the initial amount of the deposit is amount_sent'''
    assert deploy.exactAgreement(agreements_number)[4] == deposit
@pytest.mark.aaa
def test_exactAgreement_initialize_transactionCreated(deploy):
    '''check if the transactionCreated is 0'''
    assert deploy.exactAgreement(agreements_number)[5] == '0'
@pytest.mark.aaa
def test_exactAgreement_status(deploy):
    '''check if the initial status is equal to "Created"'''
    assert deploy.exactAgreement(agreements_number)[6] == 'Created'
@pytest.mark.aaa
def test_exactAgreement_time_duration(deploy):
    '''check if the initial agreement duration'''
    assert deploy.exactAgreement(agreements_number)[7] == agreement_duration

def test_new_agreement_fails_require(deploy):
    '''check if the new agreement fails, because howLong > _everyTimeUnit in the require statement'''
    try:
        chain = Chain()
        now = chain.time()
        startAgreement = now + 10000
        #length of the agreement is longer than _everyTimeUnit
        deploy.createAgreement('0xAb8483F64d9C6d1EcF9b849Ae677dD3315835cb2', 2, 500, 5, startAgreement, {'from': accounts[signee], 'value': amount_sent})
    except Exception as e:
        assert e.message[50:] == 'The period of the payment is greater than the duration of the contract'

@pytest.mark.parametrize("possibilities", [[0, 10, 15], [10, 0, 15], [10, 10, 0], [0, 0, 15], [10, 0, 0], [0, 10, 0], [0, 0, 0]])
def test_new_agreement_fails_require_larger_than_zero(possibilities, deploy):
    '''check if the creation of the new agreement fails, because the input data should be larger than 0'''
    for _ in range(7):
        try:
            chain = Chain()
            now = chain.time()
            startAgreement = now + 10000
            deploy.createAgreement('0xAb8483F64d9C6d1EcF9b849Ae677dD3315835cb2', possibilities[0], possibilities[1], possibilities[2], startAgreement, {'from': accounts[signee], 'value': amount_sent})
        except Exception as e:
            assert e.message[50:] == 'All input data must be larger than 0'

@pytest.mark.parametrize("_amount", [less_than_amount_sent[0], less_than_amount_sent[1], less_than_amount_sent[2]])    
def test_new_agreement_fails_require_msg_value_larger_than_amount(deploy, _amount):
    '''check if the creation of the new agreement fails, because the msg.value should be larger or equal to amount sent'''
    try:
        chain = Chain()
        now = chain.time()
        startAgreement = now + 10000
        deploy.createAgreement(accounts[receiver], amount_sent, every_period, agreement_duration, startAgreement, {'from': accounts[signee], 'value': _amount})
    except Exception as e:
            assert e.message[50:] == 'Deposit has to be at least the size of the amount'

def test_new_agreement_fails_require_agreementStart_larger_than_block_timestamp(deploy):
    '''check if the creation of the new agreement fails, because the _startOfTheAgreement should be larger than block.amount'''
    try:
        chain = Chain()
        now = chain.time()
        startAgreement = now - 10000
        deploy.createAgreement(accounts[receiver], amount_sent, every_period, agreement_duration, startAgreement, {'from': accounts[signee], 'value': amount_sent})
    except Exception as e:
            assert e.message[50:] == "The agreement can't be created in the past"