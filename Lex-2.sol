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
    /// @param status Representation of different stages in the agreement: Created, Activated, Terminated
    /// @param approved Confirmation of the agreedDeposit by the receiver: Not Confirmed, Confirmed
    /// @param deadline The number of days till the agreement expires
    struct Agreement{
    uint256 id; 
    address signee;
    address payable receiver; 
    uint256 amount;
    uint256 deposit;
    uint256 transactionCreated;
    string status;
    string approved;
    uint256 deadline;
  }

  /// @notice Storing the owner's address
  address public owner;

  /// @notice Using against re-entrancy
  uint16 internal locked = 1;

  /// @notice The commission we charge
  uint256 public commission = 1;

  /// @notice The commission collected
  uint256 private withdrawal_amount_owner;

  /// @notice Used to increase the id of the agreements in the "createAgreements" function
  uint numAgreement;

  constructor(){
      owner = msg.sender;
  }

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

  /// @notice Whitelisted accounts that can access withdrawal_amount_owner
  mapping(address => bool) private whitelist;


  /// @notice Emitting agreement's info 
  event AgreementInfo(
    uint256 agreementId,
    address agreementSignee, 
    address agreementReceiver, 
    uint256 agreementAmount,
    uint256 agreementDeposit,
    uint256 agreementTransactionCreated,
    string agreementStatus,
    string agreementApproved,
    uint256 agreementDeadline
  );

  /// @notice After the contract is terminated, emit an event with a message
  event Terminated(string message);

  /// @notice After other event than Terminated happens, emit it and send a message
  event NotifyUser(string message);
 
  /// @notice When an account is white- or blacklisted
  event AddedToTheList(address account);
 
  /// @notice When an account is removed from white- or blacklist
  event RemovedFromTheList(address account);


  function createAgreement(
    address payable _receiver, 
    uint256 _amount,
    uint256 _deadline,
    ) external payable {
        require(_amount > 0 && _deadline > 0, "All input data must be larger than 0");
        require(_deadline >= block.timestamp, "The agreement can't be created in the past");
        //increment the agreement id
        uint256 agreementId = numAgreement++;

        //creating a new agreement
        Agreement storage newAgreement = exactAgreement[agreementId];
        //rule for the deposit -> min is 100 wei, if larger _amount, deposit is 10% of the _amount -> bp 10
        uint256 minDeposit = 100;
        if (msg.value >= 1000){
          //check if it works
          newAgreement.deposit = msg.value * 10 / 10000;
        } else {
          newAgreement.deposit = minDeposit;
        }

        require(msg.value >= newAgreement.deposit, "Deposit needs to be 10% of the amount or at least 100 wei");

        newAgreement.id = agreementId;
        newAgreement.signee = msg.sender;
        newAgreement.receiver = _receiver;
        newAgreement.amount = _amount;

        //the status of the agreement when its created
        newAgreement.status = "Created";
        //initialize the approved term
        newAgreement.approved = "Not Confirmed";
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
          newAgreement.approved, 
          newAgreement.deadline
          ); 
  }

  function confirmAgreement(uint256 _id) external {
    if (keccak256(bytes(exactAgreement[_id].approved)) == keccak256(bytes("Confirmed"))){
		  emit NotifyUser("The agreement is already confirmed");
	  } else if (keccak256(bytes(exactAgreement[_id].status)) == keccak256(bytes("Terminated"))){
      emit NotifyUser("The agreement is already terminated");
    } else {
      require(exactAgreement[_id].receiver == msg.sender, "Only the receiver can confirm the agreement");
      //cannot confirm an agreement that ends in the past
      require(exactAgreement[_id].deadline < block.timestamp, "The agreement's deadline has ended");
      //confirm the agreement
      exactAgreement[_id].approved = "Confirmed";
      //emit that the agreement was confirmed
      emit NotifyUser("The agreement was confirmed");
	  }
  }

  function terminateContract(uint256 _id) external {
    if (keccak256(bytes(exactAgreement[_id].status)) == keccak256(bytes("Terminated"))){
		  emit NotifyUser("The agreement is already terminated");
	  } else if (exactAgreement[_id].deadline < block.timestamp){
        require(exactAgreement[_id].signee == msg.sender, "Only the signee can terminate the agreement");
        exactAgreement[_id].status = "Terminated";
        //return the deposit to the signee
        withdraw_signee[exactAgreement[_id].signee] += exactAgreement[_id].deposit;
        //ensure that the deposit is reduced to 0
        exactAgreement[_id].deposit = 0;
        emit Terminated("The agreement has been terminated");
    } else {
        require(exactAgreement[_id].signee == msg.sender, "Only the signee can terminate the agreement");
        exactAgreement[_id].status = "Terminated";
        //return the deposit to the receiver
        withdraw_receiver[exactAgreement[_id].receiver] += exactAgreement[_id].deposit;
        //ensure that the deposit is reduced to 0
        exactAgreement[_id].deposit = 0;
        emit Terminated("The agreement has been terminated");
	  }
  }

  /// @notice Receiver checking if the contract has been breached
  function wasContractBreached(uint256 _id) external {
    require(exactAgreement[_id].receiver == msg.sender, "Your logged in address isn't the same as the agreement's receiver");
    //checking if the agreement was Activated
    if (keccak256(bytes(exactAgreement[_id].status)) == keccak256(bytes("Activated"))){
      //checking if the deadline was breached
      if (exactAgreement[_id].deadline > block.timestamp){
        emit NotifyUser("The agreement wasn't breached");
      } else {
        //receiver has to wait 7 days after the breached date to withdraw the deposit
        require(exactAgreement[_id].positionPeriod + (60*60*24*7) < block.timestamp, "You can't withdraw the deposit before 7 days after breached deadline");
        //terminate the agreement
        exactAgreement[_id].status = "Terminated";
        //return deposit to receiver
        withdraw_receiver[exactAgreement[_id].receiver] += exactAgreement[_id].deposit;
        //ensure that the deposit is reduced to 0
        exactAgreement[_id].deposit = 0;
        emit Terminated("The agreement has been terminated");
      } 
    } else if (keccak256(bytes(exactAgreement[_id].status)) == keccak256(bytes("Created"))){
      if (exactAgreement[_id].deadline > block.timestamp){
        emit NotifyUser("The agreement wasn't breached");
      } else {
        //receiver has to wait 7 days after the breached date to withdraw the deposit
        require(exactAgreement[_id].positionPeriod + (60*60*24*7) < block.timestamp, "You can't withdraw the deposit before 7 days after breached deadline");
        //terminate the agreement
        exactAgreement[_id].status = "Terminated";
        //return deposit to receiver
        withdraw_receiver[exactAgreement[_id].receiver] += exactAgreement[_id].deposit;
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
	  uint256 current_amount = withdraw_signee[exactAgreement[_id].signee];
	  withdraw_signee[exactAgreement[_id].signee] = 0;
	  (bool sent, ) = exactAgreement[_id].signee.call{value: current_amount}("");
    require(sent, "Failed to send Ether");
	  emit NotifyUser("Withdrawal has been transfered");
  }

  /// @notice The receiver withdrawing the money that belongs to his/her address
  function withdrawAsTheReceiver(uint256 _id) external payable noReentrant {
    require(exactAgreement[_id].receiver == msg.sender, "Your logged in address isn't the same as the agreement's receiver");
    require(withdraw_receiver[exactAgreement[_id].receiver] > 0, "There aren't any funds to withdraw");
    uint256 current_amount = withdraw_receiver[exactAgreement[_id].receiver];
    withdraw_receiver[exactAgreement[_id].receiver] = 0;
    (bool sent, ) = exactAgreement[_id].receiver.call{value: current_amount}("");
    require(sent, "Failed to send Ether");
    emit NotifyUser("Withdrawal has been transfered");
  }
  
  /// @notice The owner withdrawing the money that belongs to his address
  function withdrawAsTheOwner() external payable noReentrant onlyWhitelisted{
		require(withdrawal_amount_owner > 0, "There aren't any funds to withdraw");
    uint256 current_amount = withdrawal_amount_owner; 
    withdrawal_amount_owner = 0;
    (bool sent, ) = msg.sender.call{value: current_amount}("");
    require(sent, "Failed to send Ether");
    emit NotifyUser("Withdrawal has been transfered");
}

  /// @notice Adding address to the whitelist
  function addToWhitelist(address _address) external onlyOwner {
    whitelist[_address] = true;
    emit AddedToTheList(_address);
  }
  
  /// @notice Removing address from the whitelist
  function removedFromWhitelist(address _address) external onlyOwner {
    whitelist[_address] = false;
    emit RemovedFromTheList(_address);
  }
  
  /// @notice Checking if the address is whitelisted
  function isWhitelisted(address _address) public view returns(bool) {
    return whitelist[_address];
  }




 fallback() external {}
 receive() external payable {}

}