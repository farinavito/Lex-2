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
    uint256 transactionCreated;
    string status;
    string approved;
    uint256 agreementStartDate;
    uint256 endPeriod;
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
    uint256 agreementTransactionCreated,
    string agreementStatus,
    string agreementApproved,
    uint256 agreementStartDate,
    uint256 agreementTimeDuration
  );

  /// @notice After the contract is terminated, emit an event with a message
  event Terminated(string message);

  /// @notice After other event than Terminated happens, emit it and send a message
  event NotifyUser(string message);
 
  /// @notice When an account is white- or blacklisted
  event AddedToTheList(address account);
 
  /// @notice When an account is removed from white- or blacklist
  event RemovedFromTheList(address account);

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