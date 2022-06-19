from itertools import chain
import pytest
import brownie
from brownie import *
from brownie import accounts
from brownie.network import rpc
from brownie.network.state import Chain

#new agreement
signee = 1
receiver = 9
amount_sent = 10**10
deposit = 100
agreement_duration = 2629743 + 1749185494
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

@pytest.fixture(scope="module", autouse=True)
def deploy(sendMoneyUntil):
    return sendMoneyUntil.deploy( {'from': accounts[0]})

@pytest.fixture(scope="module", autouse=True)
def new_agreement(deploy):
    return deploy.createAgreement(accounts[receiver], amount_sent, agreement_duration, {'from': accounts[signee], 'value': deposit})

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass



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
def test_new_agreement_fails_require_msg_value_larger_or_equal_to_100(deploy, _amount):
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
    assert deploy.exactAgreement(2)[0] == str(2)



'''TESTING MYSENDERAGREEMENTS FUNCTION'''



def test_mySenderAgreements_emits_correct_id_accounts_1(deploy):
    '''check if the mapping mySenderAgreements emits correct agreementId for the first element in the mapping of address signee'''
    assert deploy.mySenderAgreements(accounts[signee], 0) == '1'

def test_mySenderAgreements_emits_correct_id_accounts_2(deploy):
    '''check if the mapping mySenderAgreements is returning correctly the ids'''
    deploy.createAgreement(accounts[receiver], amount_sent, agreement_duration, {'from': accounts[signee], 'value': deposit})
    assert deploy.mySenderAgreements(accounts[signee], 1) == '2'



'''TESTING MYRECEIVERAGREEMENTS FUNCTION'''



def test_myReceiverAgreements_emits_correct_id_agreement_1(deploy):
    '''check if the mapping myReceiverAgreements emits correct agreementId for the first element in the mapping of address 0xAb8483F64d9C6d1EcF9b849Ae677dD3315835cb2'''
    assert deploy.myReceiverAgreements(accounts[receiver], 0) == '1'

def test_myReceiverAgreements_emits_correct_id_agreement_2(deploy):
    '''check if the mapping myReceiverAgreements is returning correctly the ids'''
    deploy.createAgreement(accounts[receiver], amount_sent, agreement_duration, {'from': accounts[signee], 'value': deposit})
    assert deploy.myReceiverAgreements(accounts[receiver], 1) == '2'



'''TESTING SENDPAYMENT, INITIALIZINGPOSITIONPERIOD AND TIMENOTBREACHED FUNCTIONS'''



@pytest.mark.parametrize("accounts_number", [without_signee[0], without_signee[1], without_signee[2]])
def test_sendPayments_fails_require_wrong_address(deploy, accounts_number):
    '''check if the sendPayments fails, because exactAgreement[_id].signee == msg.sender in the require statement'''
    try:
        #wrong signer's address
        deploy.sendPayment(agreements_number, {'from': accounts[accounts_number], 'value': amount_sent})
    except Exception as e:
        assert e.message[50:] == "Only the signee can pay the agreement's terms"

@pytest.mark.parametrize("accounts_number", [signee])
def test_sendPayments_fails_require_wrong_address_pair(deploy, accounts_number):
    '''check if the sendPayments doesn't fail, because exactAgreement[_id].signee == msg.sender in the require statement'''
    #right signer's address
    deploy.sendPayment(agreements_number, {'from': accounts[accounts_number], 'value': amount_sent})
    assert deploy.exactAgreement(agreements_number)[1] == accounts[signee]

#Checking when the agreement's status is "Created" and was sent on time and the amount sent was enough
'''
@pytest.mark.parametrize("value_sent",  [more_than_amount_sent[0], more_than_amount_sent[1], more_than_amount_sent[2]])
def test_sendPayment_value_larger_amount_withdrawal_amount_owner(deploy, deploy_addressProtector,value_sent):
    check if withdrawal_amount_owner is correctly initialized
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': value_sent})
    deploy_addressProtector.addToWhitelist(accounts[7], {'from': accounts[1]}) 
    assert deploy.getWithdrawalOwner({'from': accounts[7]}) == commission
'''
@pytest.mark.parametrize("value_sent",  [more_than_amount_sent[0], more_than_amount_sent[1], more_than_amount_sent[2]])
def test_sendPayment_value_large_amount_send_value(deploy, value_sent):
    '''check if the msg.value is sent when amount <= msg.value'''
    balance_receiver = accounts[receiver].balance() 
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': value_sent})
    deploy.withdrawAsTheReceiver(agreements_number, {'from': accounts[receiver]})
    assert accounts[receiver].balance() == balance_receiver + value_sent

@pytest.mark.parametrize("value_sent",  [more_than_amount_sent[0], more_than_amount_sent[1], more_than_amount_sent[2]])
def test_sendPayment_value_large_amount_send_value_check_signee_returned_excess(deploy, value_sent):
    '''check if the excess money is returned to the signee when he sends more than he should'''
    balance_signee = accounts[signee].balance() 
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': value_sent})
    deploy.withdrawAsTheSignee(agreements_number, {'from': accounts[signee]}) 
    assert accounts[signee].balance() == balance_signee - value_sent + (value_sent - deploy.exactAgreement(agreements_number)[3]) + deposit

@pytest.mark.parametrize("value_sent",  [amount_sent, more_than_amount_sent[0], more_than_amount_sent[1], more_than_amount_sent[2]])
def test_sendPayment_value_larger_amount_send_value_totalEtherCommited_increased(deploy, value_sent):
    '''check if totalEtherCommited increases'''
    allEth = deploy.totalEtherCommited()
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': value_sent})
    assert deploy.totalEtherCommited() == allEth + value_sent

def test_sendPayment_value_large_amount_send_value_check_signee(deploy):
    '''check if the deposit is returned to the signee'''
    balance_signee = accounts[signee].balance() 
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount_sent})
    deploy.withdrawAsTheSignee(agreements_number, {'from': accounts[signee]}) 
    assert accounts[signee].balance() + amount_sent  == balance_signee + deposit

def test_sendPayment_value_large_amount_status_Terminated(deploy):
    '''check if the status is changed to Terminated'''
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount_sent})
    assert deploy.exactAgreement(agreements_number)[6] == 'Terminated' 

def test_sendPayment_value_large_amount_emit_NotifyUser(deploy):
    '''check if the event NotifyUser is emitted when amount <= msg.value in the timeNotBreached'''
    function_initialize = deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount_sent})
    assert function_initialize.events[0][0]['message'] == "The agreement has been fullfilled"

#if msg.value < amount_sent

@pytest.mark.parametrize("value_sent",  [amount_sent])
@pytest.mark.parametrize("value_decreased",  [less_than_amount_sent[0], less_than_amount_sent[1], less_than_amount_sent[2]])
def test_sendPayment_value_large_amount_send_value_withdraw_signee(deploy, value_sent, value_decreased):
    '''check if the msg.value is not sent when amount >= msg.value in the sendPayment, the funds are returned to the signee'''
    balance_signee = accounts[signee].balance() 
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': value_sent - value_decreased})
    deploy.withdrawAsTheSignee(agreements_number, {'from': accounts[signee]}) 
    assert accounts[signee].balance() == balance_signee

@pytest.mark.parametrize("value_sent",  [amount_sent])
@pytest.mark.parametrize("value_decreased",  [less_than_amount_sent[0], less_than_amount_sent[1], less_than_amount_sent[2]])
def test_sendPayment_value_large_amount_send_value_pair_event(deploy, value_sent, value_decreased):
    '''check if the msg.value is not sent when amount <= msg.value sendPayment, the contract terminates'''
    function_initialized = deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': value_sent - value_decreased}) 
    assert function_initialized.events[0][0]['message'] == "The amount sent is lower than in the agreement"

#if the transaction wasn't sent on time

@pytest.mark.parametrize("seconds_sleep",  [more_than_agreement_duration[0], more_than_agreement_duration[1], more_than_agreement_duration[2]])
def test_sendPayment_received_on_time_false_status_terminated(deploy, seconds_sleep):
    '''check if the agreement is terminated, when transaction is sent past the agreement's duration'''
    chain = Chain()
    chain.sleep(seconds_sleep)
    deploy.sendPayment(1, {'from': accounts[signee], 'value': amount_sent})
    assert deploy.exactAgreement(1)[6] == 'Terminated'

@pytest.mark.parametrize("seconds_sleep",  [more_than_agreement_duration[0], more_than_agreement_duration[1], more_than_agreement_duration[2]])
def test_sendPayment_received_on_time_false_send_deposit(deploy, seconds_sleep):
    '''check if the deposit is sent to the receiver when transaction is sent past the agreement's duration'''
    balance_receiver = accounts[receiver].balance() 
    chain = Chain()
    chain.sleep(seconds_sleep)
    deploy.sendPayment(1, {'from': accounts[signee], 'value': 4*amount_sent}) 
    deploy.withdrawAsTheReceiver(1, {'from': accounts[receiver]})
    assert accounts[receiver].balance() == balance_receiver + deposit

@pytest.mark.parametrize("seconds_sleep",  [more_than_agreement_duration[0], more_than_agreement_duration[1], more_than_agreement_duration[2]])
def test_sendPayment_received_on_time_false_totalDepositSent(deploy, seconds_sleep):
    '''check if totalDepositSent increases by the deposit'''
    depositsTogether = deploy.totalDepositSent()
    agreementsdeposit = deploy.exactAgreement(agreements_number)[4]
    chain = Chain()
    chain.sleep(seconds_sleep) 
    deploy.sendPayment(1, {'from': accounts[signee], 'value': amount_sent}) 
    assert deploy.totalDepositSent() == depositsTogether + agreementsdeposit

@pytest.mark.parametrize("seconds_sleep",  [more_than_agreement_duration[0], more_than_agreement_duration[1], more_than_agreement_duration[2]])
def test_sendPayment_received_on_time_false_deposit_equals_zero(deploy, seconds_sleep):
    '''check if the deposit is equal zero when transaction is sent past the agreement's duration'''
    chain = Chain()
    chain.sleep(seconds_sleep)
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount_sent}) 
    assert deploy.exactAgreement(agreements_number)[5] == "0"

@pytest.mark.parametrize("seconds_sleep",  [more_than_agreement_duration[0], more_than_agreement_duration[1], more_than_agreement_duration[2]])
def test_sendPayment_received_on_time_false_return_transaction(deploy, seconds_sleep):
    '''check if the transaction is sent back to the signee when transaction is sent past the agreement's duration'''
    balance_signee = accounts[signee].balance() 
    chain = Chain()
    chain.sleep(seconds_sleep)
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount_sent}) 
    deploy.withdrawAsTheSignee(agreements_number, {'from': accounts[signee]})
    assert accounts[signee].balance() == balance_signee

@pytest.mark.parametrize("seconds_sleep",  [more_than_agreement_duration[0], more_than_agreement_duration[1], more_than_agreement_duration[2]])
def test_sendPayment_received_on_time_false_emit_Terminated(deploy, seconds_sleep):
    '''check if the event Terminated is emitted when transaction is sent past the agreement's duration'''
    chain = Chain()
    chain.sleep(seconds_sleep)
    function_initialize = deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount_sent})
    assert function_initialize.events[0][0]['message'] == "The agreement was terminated due to late payment"

#Checking when the agreement's status is "Terminated"


def test_terminateContract_emit_Terminated_initial_status_terminated(deploy):
    '''check if the sendPayments emits correctly the message when the status is "Terminated"'''
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount_sent})
    with brownie.reverts("The agreement is already terminated"):
        deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount_sent})



''' TESTING WASCONTRACTBREACHED FUNCTION '''



@pytest.mark.parametrize("wrong_accounts",  [without_receiver[0], without_receiver[1], without_receiver[2]])
def test_wasContractBreached_require_receiver_equals_wrong_account(deploy, wrong_accounts):
    '''check if the wasContractBreached fails, because exactAgreement[_id].receiver == msg.sender is the require statement'''
    with brownie.reverts("Your logged in address isn't the same as the agreement's receiver"):
        deploy.wasContractBreached(agreements_number, {'from': accounts[wrong_accounts]})

@pytest.mark.parametrize("wrong_accounts",  [without_receiver[0], without_receiver[1], without_receiver[2]])
def test_wasContractBreached_require_receiver_equals_wrong_account_2(deploy, wrong_accounts):
    '''check if the wasContractBreached fails when the contract is already terminated, because exactAgreement[_id].receiver == msg.sender is the require statement'''
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount_sent})
    with brownie.reverts("Your logged in address isn't the same as the agreement's receiver"):
        deploy.wasContractBreached(agreements_number, {'from': accounts[wrong_accounts]})

@pytest.mark.parametrize("right_accounts",  [receiver])
def test_wasContractBreached_already_terminated_status_terminated(deploy, right_accounts):
    '''check if the wasContractBreached's status terminated'''
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount_sent})
    function_initialize = deploy.wasContractBreached(agreements_number, {'from': accounts[right_accounts]})
    assert function_initialize.events[0][0]['message'] == "The agreement is already terminated"

def test_wasContractBreached_before_agreements_duration(deploy):
    '''check if the wasContractBreached called before agreement's duration period'''
    function_initialize = deploy.wasContractBreached(agreements_number, {'from': accounts[receiver]})
    assert function_initialize.events[0][0]['message'] == "The agreement wasn't breached"

@pytest.mark.parametrize("seconds_sleep",  [more_than_agreement_duration[0], more_than_agreement_duration[1], more_than_agreement_duration[2]])
def test_wasContractBreached_after_agreements_duration_status_terminated(deploy, seconds_sleep):
    '''check if the wasContractBreached's status is terminated after agreement's duration period'''
    chain = Chain()
    chain.sleep(seconds_sleep)
    deploy.wasContractBreached(agreements_number, {'from': accounts[receiver]})
    assert deploy.exactAgreement(agreements_number)[6] == 'Terminated'

@pytest.mark.parametrize("seconds_sleep",  [more_than_agreement_duration[0], more_than_agreement_duration[1], more_than_agreement_duration[2]])
def test_wasContractBreached_after_agreements_duration_send_deposit(deploy, seconds_sleep):
    '''check if the wasContractBreached returns deposit to the receiver after agreement's duration period'''
    balance_receiver = accounts[receiver].balance() 
    chain = Chain()
    chain.sleep(seconds_sleep)
    deploy.wasContractBreached(agreements_number, {'from': accounts[receiver]})
    deploy.withdrawAsTheReceiver(agreements_number, {'from': accounts[receiver]})
    assert accounts[receiver].balance() == balance_receiver + deposit

@pytest.mark.parametrize("seconds_sleep",  [more_than_agreement_duration[0], more_than_agreement_duration[1], more_than_agreement_duration[2]])
def test_wasContractBreached_after_agreements_duration_totalDepositSent(deploy, seconds_sleep):
    '''check if totalDepositSent increases by the deposit'''
    depositsTogether = deploy.totalDepositSent()
    agreementsdeposit = deploy.exactAgreement(agreements_number)[4]
    chain = Chain()
    chain.sleep(seconds_sleep)
    deploy.wasContractBreached(agreements_number, {'from': accounts[receiver]})
    assert deploy.totalDepositSent() == depositsTogether + agreementsdeposit

@pytest.mark.parametrize("seconds_sleep",  [more_than_agreement_duration[0], more_than_agreement_duration[1], more_than_agreement_duration[2]])
def test_wasContractBreached_after_agreements_duration_deposit_equals_zero(deploy, seconds_sleep):
    '''check if the deposit is equal zero when the wasContractBreached is called past the agreement's duration'''
    chain = Chain()
    chain.sleep(seconds_sleep)
    deploy.wasContractBreached(agreements_number, {'from': accounts[receiver]})
    assert deploy.exactAgreement(agreements_number)[5] == "0"

@pytest.mark.parametrize("seconds_sleep",  [more_than_agreement_duration[0], more_than_agreement_duration[1], more_than_agreement_duration[2]])
def test_sendPayment_received_on_time_false_emit_Terminated(deploy, seconds_sleep):
    '''check if the event Terminated is emitted when transaction is sent past the agreement's duration'''
    chain = Chain()
    chain.sleep(seconds_sleep)
    function_initialize = deploy.wasContractBreached(agreements_number, {'from': accounts[receiver]})
    assert function_initialize.events[0][0]['message'] == "The agreement has been terminated"



'''TEST WITHDRAWASTHERECEIVER'''



@pytest.mark.parametrize("wrong_account", [without_receiver[0], without_receiver[1], without_receiver[2]])
def test_withdrawAsTheReceiver_first_reguire_fails(deploy, wrong_account):
    '''require statement exactAgreement[_id].receiver == msg.sender fails'''
    with brownie.reverts("Your logged in address isn't the same as the agreement's receiver"):
        deploy.withdrawAsTheReceiver(agreements_number, {'from': accounts[wrong_account]})

def test_withdrawAsTheReceiver_second_reguire_fails_case_1(deploy):
    '''require statement withdraw_receiver[exactAgreement[_id].receiver] > 0 fails'''
    with brownie.reverts("There aren't any funds to withdraw"):
        deploy.withdrawAsTheReceiver(agreements_number, {'from': accounts[receiver]})

def test_withdrawAsTheReceiver_second_reguire_fails_case_2(deploy):
    '''require statement withdraw_receiver[exactAgreement[_id].receiver] > 0 fails'''
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': 4*amount_sent})
    deploy.withdrawAsTheReceiver(agreements_number, {'from': accounts[receiver]})
    with brownie.reverts("There aren't any funds to withdraw"):
        deploy.withdrawAsTheReceiver(agreements_number, {'from': accounts[receiver]})

def test_withdrawAsTheReceiver_withdrawal_sent(deploy):
    '''Check if the withdrawal was sent to receiver'''
    receiver_balance = accounts[receiver].balance()
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount_sent})
    deploy.withdrawAsTheReceiver(agreements_number, {'from': accounts[receiver]})
    assert accounts[receiver].balance() == receiver_balance + amount_sent

def test_withdrawAsTheReceiver_emit(deploy):
    '''check if it emits a message'''
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': 4*amount_sent})
    function_initialize = deploy.withdrawAsTheReceiver(agreements_number, {'from': accounts[receiver]})
    assert function_initialize.events[0][0]['message'] == "Withdrawal has been transfered"



'''TEST WITHDRAWASTHESIGNEE'''



@pytest.mark.parametrize("wrong_account", [without_signee[0], without_signee[1], without_signee[2]])
def test_withdrawAsTheSignee_first_reguire_fails(deploy, wrong_account):
    '''require statement exactAgreement[_id].signee == msg.sender fails'''
    with brownie.reverts("Your logged in address isn't the same as the agreement's signee"):
        deploy.withdrawAsTheSignee(agreements_number, {'from': accounts[wrong_account]})

def test_withdrawAsTheSignee_second_reguire_fails_case_1(deploy):
    '''require statement withdraw_receiver[exactAgreement[_id].signee] > 0 fails'''
    with brownie.reverts("There aren't any funds to withdraw"):
        deploy.withdrawAsTheSignee(agreements_number, {'from': accounts[signee]})

def test_withdrawAsTheSignee_second_reguire_fails_case_2(deploy):
    '''require statement withdraw_receiver[exactAgreement[_id].signee] > 0 fails'''
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount_sent})
    deploy.withdrawAsTheSignee(agreements_number, {'from': accounts[signee]})
    with brownie.reverts("There aren't any funds to withdraw"):
        deploy.withdrawAsTheSignee(agreements_number, {'from': accounts[signee]})

def test_withdrawAsTheSignee_withdrawal_sent_1(deploy):
    '''Check if the withdrawal is sent'''
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount_sent})
    signee_balance = accounts[signee].balance()
    deploy.withdrawAsTheSignee(agreements_number, {'from': accounts[signee]})
    assert accounts[signee].balance() == signee_balance + deposit

@pytest.mark.parametrize("amount", [more_than_amount_sent[0], more_than_amount_sent[1], more_than_amount_sent[2]])
def test_withdrawAsTheSignee_withdrawal_sent_2(deploy, amount):
    '''Check if the withdrawal and redundant amount is sent'''
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount})
    signee_balance = accounts[signee].balance()
    deploy.withdrawAsTheSignee(agreements_number, {'from': accounts[signee]})
    assert accounts[signee].balance() == signee_balance + deposit + amount - amount_sent

@pytest.mark.parametrize("amount", [more_than_amount_sent[0], more_than_amount_sent[1], more_than_amount_sent[2]])
def test_withdrawAsTheSignee_withdrawal_sent_3(deploy, amount):
    '''Check if the withdrawal is sent'''
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount})
    deploy.withdrawAsTheSignee(agreements_number, {'from': accounts[signee]})
    with brownie.reverts("There aren't any funds to withdraw"):
        deploy.withdrawAsTheSignee(agreements_number, {'from': accounts[signee]})

def test_withdrawAsTheSignee_emit(deploy):
    '''check if the event is emited'''
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount_sent})
    function_initialize = deploy.withdrawAsTheSignee(agreements_number, {'from': accounts[signee]})
    assert function_initialize.events[0][0]['message'] == "Withdrawal has been transfered"



'''TEST GETWITHDRAWALRECEIVER'''



def test_getWithdrawalReceiver_uninitialize(deploy):
    '''check if the withdraw_receiver is empty after only sending the deposit'''
    function_initialize = deploy.getWithdrawalReceiver({'from': accounts[receiver]})
    assert function_initialize == 0

def test_getWithdrawalReceiver_initialize(deploy):
    '''check if the withdraw_receiver is empty after only sending the deposit'''
    deploy.sendPayment(agreements_number, {'from': accounts[signee], 'value': amount_sent})
    function_initialize = deploy.getWithdrawalReceiver({'from': accounts[receiver]})
    assert function_initialize == amount_sent

@pytest.mark.parametrize("not_receiver", [2, 3, 4, 5])
def test_getWithdrawalReceiver_sender_doesnt_exists(deploy, not_receiver):
    '''check if msg.sender doesn't exists in withdrawal'''
    function_initialize = deploy.getWithdrawalReceiver({'from': accounts[not_receiver]})
    assert function_initialize == 0



'''TEST GETWITHDRAWALSIGNEE'''



def test_getWithdrawalSignee_initialize(deploy):
    '''check if the withdraw_signee is empty after only sending the deposit'''
    function_initialize = deploy.getWithdrawalSignee({'from': accounts[signee]})
    assert function_initialize == 0

def test_getWithdrawalSignee_uninitialize(deploy):
    '''check if the withdraw_signee is not empty after only sending the deposit'''
    function_initialize = deploy.getWithdrawalSignee({'from': accounts[signee]})
    deploy.sendPayment(agreements_number,{'from': accounts[signee], 'value': amount_sent})
    assert function_initialize + amount_sent == amount_sent
  
@pytest.mark.parametrize("not_signee", [2, 3, 4, 5])
def test_getWithdrawalSignee_sender_doesnt_exists(deploy, not_signee):
    '''check if msg.sender doesn't exists in withdrawal'''
    function_initialize = deploy.getWithdrawalSignee({'from': accounts[not_signee]})
    assert function_initialize == 0
