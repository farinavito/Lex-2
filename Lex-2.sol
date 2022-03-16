// SPDX-License-Identifier: MIT
pragma solidity 0.8.11;

/// @title Implementing a legal contract: Person A commits sending X amount to person B until Y date.
/// @author Farina Vito

contract sendMoneyUntil {
    /// @notice Defining the agreement 
    /// @param id A unique identifier of the agreement
    /// @param signee The person who commits sending the money to the receiver 
    /// @param receiver The person receiving the money
    /// @param amount The quantity of money that the signee commits sending to the receiver
    /// @param transactionCreated Unix timestamp when transaction was sent
    /// @param deposit The first transaction sent to the agreement. Initial state will be zero
    /// @param status Representation of different stages in the agreement: Created, Terminated
    /// @param deadline The number of days till the agreement expires
    struct Agreement{
    uint256 id; 
    address signee;
    address payable receiver; 
    uint256 amount;
    uint256 deposit;
    uint256 transactionCreated;
    string status;
    uint256 deadline;
  }

  /// @notice Storing the owner's address
  address internal owner;

  //add to separate smart contract
  /// @notice Storing the next in line to be an owner
  address waitingToBeOwner;

  /// @notice Using against re-entrancy
  uint16 internal locked = 1;

  /// @notice The commission we charge
  uint256 public commission = 1;

  /// @notice The commission collected
  uint256 private withdrawal_amount_owner;

  /// @notice Used to increase the id of the agreements in the "createAgreements" function
  uint public numAgreement = 1;

  /// @notice Returning the total amount of ether that was commited
  uint256 public totalEtherCommited;

  /// @notice Returning the total amount of deposit that was sent to the receiver
  uint256 public totalDepositSent;  

  //change the msg.sender to the owner of the child smart contract
  constructor(){
      owner = msg.sender;
  }

  //add to separate smart contract
  modifier onlyOwner(){
      require(msg.sender == owner, "You are not the owner");
      _;
  }

   modifier noReentrant() {
    require(locked == 1, "No re-entrancy");
    locked = 2;
    _;
    locked = 1;
  }

  //add to separate smart contract
  modifier onlyWhitelisted() {
    require(isWhitelisted(msg.sender), "You aren't whitelisted");
    _;
  }

  /// @notice Saving the money sent for the signee to withdraw it
  mapping(address => uint256) private withdraw_signee;

  /// @notice Saving the money sent for the receiver to withdraw it
  mapping(address => uint256) private withdraw_receiver;

  /// @notice A unique identifier of the agreement. The same as the id.
  mapping(uint256 => Agreement) public exactAgreement;

  /// @notice Storing the id's of the agreements that the signee has created
  mapping(address => uint[]) public mySenderAgreements;

  /// @notice Storing the id's of the agreements of the same receiver address
  mapping(address => uint[]) public myReceiverAgreements;

  //add to separate smart contract
  /// @notice Whitelisted accounts that can access withdrawal_amount_owner
  mapping(address => bool) internal whitelist;


  /// @notice Emitting agreement's info 
  event AgreementInfo(
    uint256 agreementId,
    address agreementSignee, 
    address agreementReceiver, 
    uint256 agreementAmount,
    uint256 agreementDeposit,
    uint256 agreementTransactionCreated,
    string agreementStatus,
    uint256 agreementDeadline
  );

  /// @notice After the contract is terminated, emit an event with a message
  event Terminated(string message);

  /// @notice After other event than Terminated happens, emit it and send a message
  event NotifyUser(string message);
 
 //add to separate smart contract
  /// @notice When an account is whitelisted
  event AddedToTheList(address account);
 
 //add to separate smart contract
  /// @notice When an account is removed from whitelist
  event RemovedFromTheList(address account);

  /// @notice Creating an agreement and sending the deposit
  function createAgreement(
    address payable _receiver, 
    uint256 _amount,
    uint256 _deadline
    ) external payable {
        require(_amount > 0 && _deadline > 0, "All input data must be larger than 0");
        require(_deadline >= block.timestamp, "The agreement can't be created in the past");
        //rule for the deposit -> min is 100 wei, if larger _amount, deposit is 10% of the _amount -> bp 10
        uint256 storeDeposit;
        uint256 minDeposit = 100;
        if (msg.value >= 1000){
          //check if it works
          storeDeposit = msg.value * 10 / 10000;
        } else {
          storeDeposit = minDeposit;
        }

        require(msg.value >= storeDeposit, "Deposit needs to be 10% of the amount or at least 100 wei");

        //increment the agreement id
        uint256 agreementId = numAgreement++;
        //creating a new agreement
        Agreement storage newAgreement = exactAgreement[agreementId];
        newAgreement.id = agreementId;
        newAgreement.signee = msg.sender;
        newAgreement.receiver = _receiver;
        newAgreement.amount = _amount;
        newAgreement.deposit = storeDeposit;

        //the status of the agreement when its created
        newAgreement.status = "Created";
        //how long will the agreement last
        newAgreement.deadline = _deadline;
        //storing the ids of the agreements and connecting them to msg.sender's address so we can display them to the frontend
        mySenderAgreements[msg.sender].push(agreementId);
        //storing the ids of the agreements and connecting them to _receiver's address so we can display them to the frontend
        myReceiverAgreements[_receiver].push(agreementId);

        emit AgreementInfo(
          newAgreement.id, 
          newAgreement.signee, 
          newAgreement.receiver, 
          newAgreement.amount,
          newAgreement.deposit,
          newAgreement.transactionCreated, 
          newAgreement.status,
          newAgreement.deadline
          ); 
  }

  /// @notice Sending the payment based on the status of the agreement
  function sendPayment(uint256 _id) external payable {
    require(exactAgreement[_id].signee == msg.sender, "Only the owner can pay the agreement's terms");
    if (keccak256(bytes(exactAgreement[_id].status)) == keccak256(bytes("Created"))){
      //if the deadline wasn't breached
      if (exactAgreement[_id].deadline > block.timestamp){
        //if the amount sent wasn't enough
        if (exactAgreement[_id].amount <= msg.value){
          //storing the amount sent subtracted by commission
          uint256 changedAmount;
          changedAmount = msg.value - commission;
          //adding the commission to a owner's withdrawal
          withdrawal_amount_owner += commission;
          //send the transaction to the receiver
          withdraw_receiver[exactAgreement[_id].receiver] += changedAmount;
          //returning any access ethers sent to the sender
          withdraw_signee[exactAgreement[_id].signee] += msg.value - exactAgreement[_id].amount;
          //change the total amount of ether sent
          totalEtherCommited += changedAmount;
          //returning the deposit to the signee
          withdraw_signee[exactAgreement[_id].signee] += exactAgreement[_id].deposit;
          //terminate the agreement
          exactAgreement[_id].status = "Terminated";
          emit NotifyUser("The agreement has been fullfilled"); 
        //if the transaction was on time, but it wasn't enough
        } else {
            //return the transaction to the signee
            withdraw_signee[exactAgreement[_id].signee] += msg.value;
            emit NotifyUser("The amount sent is lower than in the agreement");      
        }
      //if the transaction wasn't sent on time
      } else {
        exactAgreement[_id].status = "Terminated";
        //sending the deposit to the receiver
        withdraw_receiver[exactAgreement[_id].receiver] += exactAgreement[_id].deposit;
        //change the total amount of deposit sent to the receiver
        totalDepositSent += exactAgreement[_id].deposit;
        //ensure that the deposit is reduced to 0
        exactAgreement[_id].deposit = 0;
        //return the transaction to the signee
        withdraw_signee[exactAgreement[_id].signee] += msg.value;
        emit Terminated("The agreement was terminated due to late payment");
      }
    } else if (keccak256(bytes(exactAgreement[_id].status)) == keccak256(bytes("Terminated"))){
          //return the transaction to the signee
          revert("The agreement is already terminated");
    } else {
          //return the transaction to the signee
          revert("There is no agreement with this id");
    }
  }

  /// @notice Receiver checking if the contract has been breached
  function wasContractBreached(uint256 _id) external {
    require(exactAgreement[_id].receiver == msg.sender, "Your logged in address isn't the same as the agreement's receiver");
    if (keccak256(bytes(exactAgreement[_id].status)) == keccak256(bytes("Created"))){
      if (exactAgreement[_id].deadline > block.timestamp){
        emit NotifyUser("The agreement wasn't breached");
      } else {
        //terminate the agreement
        exactAgreement[_id].status = "Terminated";
        //return deposit to receiver
        withdraw_receiver[exactAgreement[_id].receiver] += exactAgreement[_id].deposit;
        //change the total amount of deposit sent to the receiver
        totalDepositSent += exactAgreement[_id].deposit;
        //ensure that the deposit is reduced to 0
        exactAgreement[_id].deposit = 0;
        emit Terminated("The agreement has been terminated");
      }
    } else {
        emit NotifyUser("The agreement is already terminated");
    }
  } 

  /// @notice The signee withdrawing the money that belongs to his/her address
  function withdrawAsTheSignee(uint256 _id) external payable noReentrant {
	  require(exactAgreement[_id].signee == msg.sender, "Your logged in address isn't the same as the agreement's signee");
    require(withdraw_signee[exactAgreement[_id].signee] > 0, "There aren't any funds to withdraw");	  
	  (bool sent, ) = exactAgreement[_id].signee.call{value: withdraw_signee[exactAgreement[_id].signee]}("");
    require(sent, "Failed to send Ether");
    withdraw_signee[exactAgreement[_id].signee] = 0;
	  emit NotifyUser("Withdrawal has been transfered");
  }

  /// @notice The receiver withdrawing the money that belongs to his/her address
  function withdrawAsTheReceiver(uint256 _id) external payable noReentrant {
    require(exactAgreement[_id].receiver == msg.sender, "Your logged in address isn't the same as the agreement's receiver");
    require(withdraw_receiver[exactAgreement[_id].receiver] > 0, "There aren't any funds to withdraw");    
    (bool sent, ) = exactAgreement[_id].receiver.call{value: withdraw_receiver[exactAgreement[_id].receiver]}("");
    require(sent, "Failed to send Ether");
    withdraw_receiver[exactAgreement[_id].receiver] = 0;
    emit NotifyUser("Withdrawal has been transfered");
  }
  
  /// @notice The owner withdrawing the money that belongs to his address
  function withdrawAsTheOwner() external payable noReentrant onlyWhitelisted{
		require(withdrawal_amount_owner > 0, "There aren't any funds to withdraw");
    (bool sent, ) = msg.sender.call{value: withdrawal_amount_owner}("");
    require(sent, "Failed to send Ether");
    withdrawal_amount_owner = 0;
    emit NotifyUser("Withdrawal has been transfered");
  }

  /// @notice Return the withdrawal amount of the agreement's signee
  function getWithdrawalSignee(uint256 _id) external view returns(uint256){
    require(exactAgreement[_id].signee == msg.sender, "Your logged in address isn't the same as the agreement's signee");
    return withdraw_signee[exactAgreement[_id].signee];
  }

  /// @notice Return the withdrawal amount of the agreement's receiver
  function getWithdrawalReceiver(uint256 _id) external view returns(uint256){
    require(exactAgreement[_id].receiver == msg.sender, "Your logged in address isn't the same as the agreement's receiver");
    return withdraw_receiver[exactAgreement[_id].receiver];
  }

  /// @notice Return the withdrawal amount of the owner
  function getWithdrawalOwner() external view onlyWhitelisted returns(uint256){
    return withdrawal_amount_owner;
  }
  
  /// @notice Changing the commission
  function changeCommission(uint256 _newCommission) external onlyWhitelisted {
		require(_newCommission > 0 && _newCommission < 10*15 + 1, "Commission doesn't follow the rules");
		commission = _newCommission;
		emit NotifyUser("Commission changed");
	}

  //add to separate smart contract
  /// @notice Adding address to the whitelist
  function addToWhitelist(address _address) external onlyOwner {
    whitelist[_address] = true;
    emit AddedToTheList(_address);
  }
  
  //add to separate smart contract
  /// @notice Removing address from the whitelist
  function removedFromWhitelist(address _address) external onlyOwner {
    whitelist[_address] = false;
    emit RemovedFromTheList(_address);
  }
  
  //add to separate smart contract
  /// @notice Checking if the address is whitelisted
  function isWhitelisted(address _address) internal view returns(bool) {
    return whitelist[_address];
  }

  //add to separate smart contract
  /// @notice Checking if the address is whitelisted by the same address
  function isWhitelistedExternal(address _address) external view onlyWhitelisted returns(bool) {
    return whitelist[_address];
  }

  //add to separate smart contract
  //create functionality that _nextInLine needs to be approved by multisig, if it's not, you can't change owner
  /// @notice Changing the owner and the waitingToBeOwner
  function changeOwner(addres _nextInline) external {
    require(waitingToBeOwner == msg.sender, "You don't have permissions");
    require(waitingToBeOwner != _nextInline);
    owner = waitingToBeOwner;
    waitingToBeOwner = _nextInline;
  }


 fallback() external {}
 receive() external payable {}

}