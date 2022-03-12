// SPDX-License-Identifier: MIT
pragma solidity 0.8.11;

/// @title Implementing a legal contract: Person A commits sending X amount to person B until Y date.
/// @author Farina Vito

contract sendMoneyUntil {

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
        require(msg.value >= _amount, "Deposit has to be at least the size of the amount");
        require(_deadline >= block.timestamp, "The agreement can't be created in the past");
        uint256 agreementId = numAgreement++;

        //creating a new agreement
        Agreement storage newAgreement = exactAgreement[agreementId];
        //rule for the deposit -> min is 100 wei, if larger _amount, deposit is 10% of the _amount
        uint256 minDeposit = 100;
        if (msg.value >= minDeposit){

        } else {

        }

        newAgreement.id = agreementId;
        newAgreement.signee = msg.sender;
        newAgreement.receiver = _receiver;
        newAgreement.amount = _amount;

        //the amount that is actually deposited to the agreement. We initialize it with 0
        newAgreement.deposit = msg.value;
        //the status of the agreement when its created
        newAgreement.status = "Created";
        //initialize the approved term
        newAgreement.approved = "Not Confirmed";
        //when was the agreement created
        newAgreement.agreementStartDate= _startOfTheAgreement;
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