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
negative_values = [-1, -10, -100]

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
    

signee_2 = signee
receiver_2 = receiver
amount_sent_2 = 10**5
deposit_2 = 100
agreement_duration_2 = 31556926 + 1649185494
initial_howLong_2 = 364
agreements_number_2 = 2

@pytest.fixture(autouse=True)
def new_agreement_2(deploy, module_isolation):
    return deploy.createAgreement(accounts[receiver_2], amount_sent_2, agreement_duration_2, {'from': accounts[signee_2], 'value': deposit_2})



'''TESTING CREATEAGREEMENT AGREEMENT 1'''



def test_exactAgreement_id(deploy):
    '''check if the first id of the agreement is zero'''
    assert deploy.exactAgreement(agreements_number)[0] == str(agreements_number)

def test_exactAgreement_signee(deploy):
    '''check if the first address of the agreement's signee is the same as the signee'''
    assert deploy.exactAgreement(agreements_number)[1] == accounts[signee]

def test_exactAgreement_receiver(deploy):
    '''check if the first address of the agreement's receiver is the same as the accounts[0]'''
    assert deploy.exactAgreement(agreements_number)[2] == accounts[receiver]

def test_exactAgreement_amount(deploy):
    '''check if the amount of the agreement is 2'''
    assert deploy.exactAgreement(agreements_number)[3] == amount_sent  

def test_exactAgreement_deposit(deploy):
    '''check if the initial amount of the deposit is amount_sent'''
    assert deploy.exactAgreement(agreements_number)[4] == deposit

def test_exactAgreement_initialize_transactionCreated(deploy):
    '''check if the transactionCreated is 0'''
    assert deploy.exactAgreement(agreements_number)[5] == '0'

def test_exactAgreement_status(deploy):
    '''check if the initial status is equal to "Created"'''
    assert deploy.exactAgreement(agreements_number)[6] == 'Created'

def test_exactAgreement_time_duration(deploy):
    '''check if the initial agreement duration'''
    assert deploy.exactAgreement(agreements_number)[7] == agreement_duration

@pytest.mark.parametrize("possibilities", [[0, 10], [10, 0], [0, 0]])
def test_new_agreement_fails_require_larger_than_zero(possibilities, deploy):
    '''check if the creation of the new agreement fails, because the input data should be larger than 0'''
    try:
        deploy.createAgreement('0xAb8483F64d9C6d1EcF9b849Ae677dD3315835cb2', possibilities[0], possibilities[1], {'from': accounts[signee], 'value': deposit})
    except Exception as e:
        assert e.message[50:] == 'All input data must be larger than 0'

def test_new_agreement_fails_require_agreementStart_larger_than_deadline(deploy):
    '''check if the creation of the new agreement fails, because the _deadline should be larger than block.amount'''
    try:
        chain = Chain()
        now = chain.time()
        endAgreement = now - 10000
        deploy.createAgreement(accounts[receiver], amount_sent, endAgreement, {'from': accounts[signee], 'value': deposit})
    except Exception as e:
            assert e.message[50:] == "The agreement can't be created in the past"

@pytest.mark.parametrize("_amount", [0, 1, 10, 80, 99])
def test_new_agreement_fails_require_msg_value_larger_or_equal_to_zero(deploy, _amount):
    '''check if the creation of the new agreement fails, because the msg.value should be larger or equal to 100'''
    try:
        deploy.createAgreement(accounts[receiver], amount_sent, agreement_duration, {'from': accounts[signee], 'value': _amount})
    except Exception as e:
            assert e.message[50:] == 'Deposit needs to be 10% of the amount or at least 100 wei'

@pytest.mark.parametrize("_deposit", [999])
@pytest.mark.parametrize("_amount", [101, 150, 200, 800, 999, 1000])
def test_new_agreement_fails_require_msg_value_larger_or_equal_to_10_percentage(deploy, _amount, _deposit):
    '''check if the creation of the new agreement fails, because the msg.value is larger than 100, but it's not 10%'''
    deploy.createAgreement(accounts[receiver], _deposit, agreement_duration, {'from': accounts[signee], 'value': _amount})
    assert deploy.exactAgreement(3)[0] == str(3)




'''TESTING CREATEAGREEMENT FUNCTION AGREEMENT 2'''



def test_exactAgreement_id(deploy):
    '''check if the first id of the agreement is zero'''
    assert deploy.exactAgreement(agreements_number_2)[0] == str(agreements_number_2)

def test_exactAgreement_signee(deploy):
    '''check if the first address of the agreement's signee is the same as the signee'''
    assert deploy.exactAgreement(agreements_number_2)[1] == accounts[signee_2]

def test_exactAgreement_receiver(deploy):
    '''check if the first address of the agreement's receiver is the same as the accounts[0]'''
    assert deploy.exactAgreement(agreements_number_2)[2] == accounts[receiver_2]

def test_exactAgreement_amount(deploy):
    '''check if the amount of the agreement is 2'''
    assert deploy.exactAgreement(agreements_number_2)[3] == amount_sent_2  

def test_exactAgreement_deposit(deploy):
    '''check if the initial amount of the deposit is amount_sent'''
    assert deploy.exactAgreement(agreements_number_2)[4] == deposit_2

def test_exactAgreement_initialize_transactionCreated(deploy):
    '''check if the transactionCreated is 0'''
    assert deploy.exactAgreement(agreements_number_2)[5] == '0'

def test_exactAgreement_status(deploy):
    '''check if the initial status is equal to "Created"'''
    assert deploy.exactAgreement(agreements_number_2)[6] == 'Created'

def test_exactAgreement_time_duration(deploy):
    '''check if the initial agreement duration'''
    assert deploy.exactAgreement(agreements_number_2)[7] == agreement_duration_2