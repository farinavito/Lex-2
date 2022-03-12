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
}