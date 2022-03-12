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



}