

WHY
---

I see smart contracts as means of resolving one of the most difficult problems - How can I trust someone I don't know and with whom I don't have physical contact that her/his actions will back up what we have agreed upon?
I think by creating a system that allows us to trust one another even if we are complete strangers will eventually lead to new and far better relationships between subjects, consequently to new economies - ones that we haven't seen before.
Just imagine how this could help to create a new world. A world were trusting strangers will be taken for granted. 

-------------------------------------------------
* How does this smart contract follow the above?
-------------------------------------------------
It enables you to commit sending a specific amount of money until a predetermined date. This is how we have enabled a commitment between two parties, otherwise the sender will loose the deposit.

SHORT SUMMARY OF INTENDED USE
------------------------------

-----------------------------------------------
* What this smart contract should be used for?
-----------------------------------------------
I invision it to be used for one-time commitment to pay the other party. 

---------------------------------------------------
* What this smart contract SHOULD NOT be used for?
---------------------------------------------------
It shouldn't be used for any agreements where one subject commits sending money and other providing services and goods for the received money. 
This smart contract DOESN'T have an implementation of checking if the payer is receiving goods or services for his/her money.
The purpose of this smart contract is to check if the subject who commited sending money really does that. Otherwise, the deposit will be sent to the receiver.

---------------------------------------------------------------
* Short step by step summary on how to use this smart contract:
----------------------------------------------------------------
	1) The sender creates an agreement where he/she defines the receiver's address, the amount of money he/she commits sending and the deadline of payment.
	   Additionally, the sender will have to send minimal 100 wei. If the commited amount of money to pay is larger than 100 wei, deposit is 10% of this amount. This amount will be used as the deposit, which will be sent to the receiver if the agreement is breached.
	   The sender will get back the deposit if he/she fulfills his/her obligations in the agreement.
	2) Now the agreement is activated. The sender needs to fulfill his/her obligations in the agreement by sending the right amount of money in the correct time period. Otherwise, he/she will loose the deposit. 
	3) The receiver can check if the agreement was breached by calling wasContractBreached function. He/She will received the deposit in the case of a breach.
	4) Once the sender sends the agreed amount, the contract will be terminated and he/she will be able to retrieve his/her deposit.
	5) The sender and receiver can withdraw the money that belongs to them by calling a withdraw function.

------------------------------------------------------------------
* Why are there 2 contracts in this repo?
------------------------------------------------------------------
This contract is attended to be deployed with AddressProtector smart contract, which provides more safety towards people who deploy smart contract. If you want to learn more, please check our ProtectSmartContracts repository
