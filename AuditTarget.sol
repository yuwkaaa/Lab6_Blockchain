// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

// NT547 - Lab 06 - Hop dong rieng cua MSSV 24521113. KHONG deploy len mainnet.

interface IERC20Like {
    function transfer(address to, uint256 amount) external returns (bool);
}

contract StakingPool_1113 {
    address public owner;
    mapping(address => uint256) public shares;
    IERC20Like public payToken;
    mapping(address => uint256) public points;
    uint256 public nextRelease;
    bool private entered;
    mapping(address => uint256) public safeBalances;

    event Deposited(address indexed who, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    modifier oneAtATime() {
        require(!entered, "reentrant");
        entered = true;
        _;
        entered = false;
    }

    constructor() {
        owner = msg.sender;
    }

    function stake() external payable {
        shares[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    function ownerWithdraw(uint256 amount) external onlyOwner {
        (bool ok, ) = payable(owner).call{value: amount}("");
        require(ok, "withdraw failed");
    }

    function setRewardToken(address t) external onlyOwner {
        require(t != address(0), "zero");
        payToken = IERC20Like(t);
    }

    function convertRewards(uint256 amount) external {
        require(points[msg.sender] >= amount, "not enough");
        points[msg.sender] -= amount;
        require(payToken.transfer(msg.sender, amount), "transfer failed");
    }

    function setAdmin(address newOwner) external {
        require(tx.origin == owner, "not owner");
        require(newOwner != address(0), "zero");
        owner = newOwner;
    }

    function destroyPool() external onlyOwner {
        (bool ok, ) = payable(owner).call{value: address(this).balance}("");
        require(ok, "drain failed");
    }

    function releaseTenth() external onlyOwner {
        require(block.timestamp >= nextRelease, "locked");
        nextRelease = block.timestamp + 1 days;
        (bool ok, ) = payable(owner).call{value: address(this).balance / 10}("");
        require(ok, "release failed");
    }

    function splitDeposit(address[] calldata receivers) external payable {
        uint256 n = receivers.length;
        require(n > 0, "empty receivers");
        require(msg.value % n == 0, "indivisible amount");
        uint256 each = msg.value / n;
        for (uint256 i = 0; i < n; i++) {
            shares[receivers[i]] += each;
        }
    }

    function stakeSafe() external payable oneAtATime {
        safeBalances[msg.sender] += msg.value;
    }

    // slither-disable-next-line reentrancy-eth
    function claimSafe() external oneAtATime {
        uint256 a = safeBalances[msg.sender];
        (bool ok, ) = msg.sender.call{value: a}("");
        require(ok, "send failed");
        safeBalances[msg.sender] = 0;
    }
}
