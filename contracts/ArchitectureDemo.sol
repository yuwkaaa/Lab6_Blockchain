// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

// File nay cung cap san cho bai printer; KHONG can lab NFT cua buoi truoc.
abstract contract AccessManaged {
    address public admin;
    constructor() { admin = msg.sender; }
    modifier onlyAdmin() { require(msg.sender == admin, "admin only"); _; }
}
contract BalanceLedger {
    mapping(address => uint256) internal balances;
    function balanceOf(address account) external view returns (uint256) {
        return balances[account];
    }
    function _credit(address account, uint256 amount) internal {
        balances[account] += amount;
    }
}
contract StudentAsset is AccessManaged, BalanceLedger {
    event Mint(address indexed to, uint256 amount);
    function mint(address to, uint256 amount) external onlyAdmin {
        require(to != address(0), "zero");
        _credit(to, amount);
        emit Mint(to, amount);
    }
}
