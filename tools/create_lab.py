#!/usr/bin/env python3
# NT547 Lab06. Synthesize a deterministic, unique-for-MSSV audit target.
# This script does NOT contain the teacher answer key or remediation.
import argparse, datetime, hashlib, json, random, re, secrets
from pathlib import Path
POOLS = {'contract': ['StakingPool',
              'CrowdFund',
              'PiggyBank',
              'LotteryHub',
              'TipJar',
              'Escrow',
              'Treasury',
              'SavingsClub'],
 'bal': ['balances', 'deposits', 'credit', 'ledger', 'stakes', 'shares'],
 'deposit': ['deposit', 'fund', 'stake', 'contribute', 'topUp', 'save'],
 'withdraw': ['withdraw', 'claim', 'cashOut', 'redeem', 'pullFunds', 'exitPool'],
 'setOwner': ['changeOwner', 'setAdmin', 'transferControl', 'updateOwner', 'handOver'],
 'kill': ['shutdown', 'closeVault', 'terminate', 'destroyPool', 'sunset'],
 'payout': ['payout', 'sendReward', 'distribute', 'refundTo', 'grant'],
 'sweep': ['sweep', 'flush', 'rescueEth', 'collectFees', 'drainTo'],
 'exec': ['execute', 'forward', 'proxyCall', 'runModule', 'plugin'],
 'players': ['players', 'entrants', 'tickets', 'participants'],
 'join': ['join', 'enter', 'buyTicket', 'register'],
 'draw': ['draw', 'pickWinner', 'settle', 'roll'],
 'token': ['rewardToken', 'usdt', 'stableCoin', 'payToken'],
 'setToken': ['setRewardToken', 'configureToken', 'setPayToken'],
 'credits': ['points', 'rewards', 'vouchers', 'tokenCredit'],
 'redeemTok': ['redeemPoints', 'claimTokens', 'convertRewards', 'withdrawToken'],
 'treasury': ['treasury', 'feeWallet', 'vaultKeeper', 'beneficiary'],
 'flushTreasury': ['payTreasury', 'forwardFees', 'settleFees', 'moveToTreasury'],
 'airdrop': ['airdrop', 'batchCredit', 'splitDeposit', 'multiFund'],
 'used': ['usedIds', 'claimedKeys', 'seenVouchers', 'redeemed'],
 'claimId': ['claimVoucher', 'useCode', 'redeemCode', 'activate'],
 'feeBps': ['feeBps', 'rateBps', 'cutBps', 'taxBps'],
 'quote': ['quoteFee', 'calcFee', 'previewFee', 'feeOf'],
 'unlockAt': ['unlockAt', 'nextRelease', 'cooldownEnd', 'releaseTime'],
 'release': ['releaseTenth', 'vestStep', 'periodicRelease', 'drip'],
 'dayIdx': ['dayOfWeek', 'weekdayIndex', 'uiDay', 'displayDay'],
 'isEmpty': ['isEmpty', 'vaultDrained', 'noFunds', 'zeroBalance'],
 'lock': ['locked', 'entered', 'busy', 'mutex'],
 'guard': ['guarded', 'oneAtATime', 'exclusive', 'serial'],
 'dep2': ['depositSafe', 'fundSafe', 'stakeSafe', 'saveSafe'],
 'bal2': ['safeBalances', 'escrowed', 'held', 'parked'],
 'wd2': ['withdrawSafe', 'claimSafe', 'exitSafe', 'redeemSafe']}
BANK_A = {'V01_reentrancy': {'code': '    function {withdraw}() external {{\n'
                            '        uint256 amount = {bal}[msg.sender];\n'
                            '        require(amount > 0, "empty");\n'
                            '        (bool ok, ) = msg.sender.call{{value: amount}}("");\n'
                            '        require(ok, "send failed");\n'
                            '        {bal}[msg.sender] = 0;\n'
                            '    }}\n'},
 'V02_tx_origin': {'code': '    function {setOwner}(address newOwner) external {{\n'
                           '        require(tx.origin == owner, "not owner");\n'
                           '        require(newOwner != address(0), "zero");\n'
                           '        owner = newOwner;\n'
                           '    }}\n'},
 'V03_suicidal': {'code': '    function {kill}() external {{\n'
                          '        selfdestruct(payable(msg.sender));\n'
                          '    }}\n'},
 'V04_arbitrary_send': {'code': '    function {payout}(address payable to, uint256 amount) external {{\n'
                                '        to.transfer(amount);\n'
                                '    }}\n'},
 'V05_unchecked_lowlevel': {'code': '    function {sweep}(address payable to) external onlyOwner {{\n'
                                    '        require(to != address(0), "zero");\n'
                                    '        to.call{{value: address(this).balance}}("");\n'
                                    '    }}\n'},
 'V06_delegatecall': {'code': '    function {exec}(address target, bytes calldata data) external {{\n'
                              '        (bool ok, ) = target.delegatecall(data);\n'
                              '        require(ok, "delegatecall failed");\n'
                              '    }}\n'},
 'V07_weak_prng': {'state': '    address[] public {players};\n',
                   'code': '    function {join}() external payable {{\n'
                           '        require(msg.value == 0.01 ether, "0.01 ETH");\n'
                           '        {players}.push(msg.sender);\n'
                           '    }}\n'
                           '\n'
                           '    function {draw}() external onlyOwner {{\n'
                           '        require({players}.length > 0, "no players");\n'
                           '        uint256 idx = block.timestamp % {players}.length;\n'
                           '        address winner = {players}[idx];\n'
                           '        delete {players};\n'
                           '        (bool ok, ) = payable(winner).call{{value: address(this).balance}}("");\n'
                           '        require(ok, "prize failed");\n'
                           '    }}\n'},
 'V08_unchecked_transfer': {'state': '    IERC20Like public {token};\n'
                                     '    mapping(address => uint256) public {credits};\n',
                            'code': '    function {setToken}(address t) external onlyOwner {{\n'
                                    '        require(t != address(0), "zero");\n'
                                    '        {token} = IERC20Like(t);\n'
                                    '    }}\n'
                                    '\n'
                                    '    function {redeemTok}(uint256 amount) external {{\n'
                                    '        require({credits}[msg.sender] >= amount, "not enough");\n'
                                    '        {credits}[msg.sender] -= amount;\n'
                                    '        {token}.transfer(msg.sender, amount);\n'
                                    '    }}\n'},
 'V09_uninitialized_state': {'state': '    address payable internal {treasury};\n',
                             'code': '    function {flushTreasury}() external onlyOwner {{\n'
                                     '        {treasury}.transfer(address(this).balance / 2);\n'
                                     '    }}\n'},
 'V10_msg_value_loop': {'code': '    function {airdrop}(address[] calldata receivers) external payable {{\n'
                                '        for (uint256 i = 0; i < receivers.length; i++) {{\n'
                                '            {bal}[receivers[i]] += msg.value;\n'
                                '        }}\n'
                                '    }}\n'},
 'V11_encode_packed': {'state': '    mapping(bytes32 => bool) public {used};\n',
                       'code': '    function {claimId}(string calldata campaign, string calldata code) '
                               'external {{\n'
                               '        bytes32 id = keccak256(abi.encodePacked(campaign, code));\n'
                               '        require(!{used}[id], "used");\n'
                               '        {used}[id] = true;\n'
                               '        {bal}[msg.sender] += 1;\n'
                               '    }}\n'},
 'V12_divide_before_multiply': {'state': '    uint256 public {feeBps} = 250;\n',
                                'code': '    function {quote}(uint256 amount) public view returns (uint256) '
                                        '{{\n'
                                        '        return amount / 10000 * {feeBps};\n'
                                        '    }}\n'}}
BANK_B = {'F1_timelock': {'state': '    uint256 public {unlockAt};\n',
                 'code': '    function {release}() external onlyOwner {{\n'
                         '        require(block.timestamp >= {unlockAt}, "locked");\n'
                         '        {unlockAt} = block.timestamp + 1 days;\n'
                         '        (bool ok, ) = payable(owner).call{{value: address(this).balance / '
                         '10}}("");\n'
                         '        require(ok, "release failed");\n'
                         '    }}\n'},
 'F2_weekday': {'code': '    function {dayIdx}() external view returns (uint256) {{\n'
                        '        return (block.timestamp / 1 days + 4) % 7;\n'
                        '    }}\n'},
 'F3_strict_equality_view': {'code': '    function {isEmpty}() external view returns (bool) {{\n'
                                     '        return address(this).balance == 0;\n'
                                     '    }}\n'},
 'F4_guarded_reentrancy': {'state': '    bool private {lock};\n'
                                    '    mapping(address => uint256) public {bal2};\n',
                           'modifier': '    modifier {guard}() {{\n'
                                       '        require(!{lock}, "reentrant");\n'
                                       '        {lock} = true;\n'
                                       '        _;\n'
                                       '        {lock} = false;\n'
                                       '    }}\n',
                           'code': '    function {dep2}() external payable {guard} {{\n'
                                   '        {bal2}[msg.sender] += msg.value;\n'
                                   '    }}\n'
                                   '\n'
                                   '    function {wd2}() external {guard} {{\n'
                                   '        uint256 a = {bal2}[msg.sender];\n'
                                   '        (bool ok, ) = msg.sender.call{{value: a}}("");\n'
                                   '        require(ok, "send failed");\n'
                                   '        {bal2}[msg.sender] = 0;\n'
                                   '    }}\n'}}

def generate(mssv):
    m = int(mssv)
    rng = random.Random(m * 7919 + 547)
    names = {k: rng.choice(v) for k,v in POOLS.items()}
    names['contract'] = f"{names['contract']}_{m % 10000:04d}"
    chosen = sorted(rng.sample(sorted(BANK_A),4))
    # Always include one stable Medium detector for a reproducible CI baseline RED.
    if 'V02_tx_origin' not in chosen:
        chosen[-1] = 'V02_tx_origin'
    ids = sorted(chosen) + sorted(rng.sample(sorted(BANK_B),2))
    parts = [(k, (BANK_A.get(k) or BANK_B.get(k))) for k in ids]
    rng.shuffle(parts)
    lines = [
        '// SPDX-License-Identifier: MIT',
        'pragma solidity 0.8.24;',
        '',
        f'// NT547 - Lab 06 - Hop dong rieng cua MSSV {m}. KHONG deploy len mainnet.',
        '',
        'interface IERC20Like {',
        '    function transfer(address to, uint256 amount) external returns (bool);',
        '}',
        '',
        f"contract {names['contract']} {{",
        '    address public owner;',
        f"    mapping(address => uint256) public {names['bal']};",
    ]
    for _, item in parts:
        if item.get('state'):
            lines += item['state'].format(**names).rstrip('\n').split('\n')
    lines += ['', '    event Deposited(address indexed who, uint256 amount);', '',
              '    modifier onlyOwner() {', '        require(msg.sender == owner, "not owner");', '        _;', '    }', '']
    for _,item in parts:
        if item.get('modifier'):
            lines += item['modifier'].format(**names).rstrip('\n').split('\n') + ['']
    lines += ['    constructor() {', '        owner = msg.sender;', '    }', '',
              f"    function {names['deposit']}() external payable {{",
              f"        {names['bal']}[msg.sender] += msg.value;",
              '        emit Deposited(msg.sender, msg.value);', '    }', '',
              '    function ownerWithdraw(uint256 amount) external onlyOwner {',
              '        (bool ok, ) = payable(owner).call{value: amount}("");',
              '        require(ok, "withdraw failed");', '    }', '']
    for _,item in parts:
        lines += item['code'].format(**names).rstrip('\n').split('\n') + ['']
    while lines[-1] == '': lines.pop()
    lines.append('}')
    return '\n'.join(lines) + '\n', names['contract']

def main():
    parser = argparse.ArgumentParser(description='Tao AuditTarget.sol tu MSSV, khong can GV cap ma.')
    parser.add_argument('mssv', help='MSSV 7-10 chu so')
    parser.add_argument('--out',default='.',help='thu muc ket qua')
    parser.add_argument('--force',action='store_true',help='ghi de target (KHONG dung sau khi sua)')
    a=parser.parse_args()
    if not re.fullmatch(r'[0-9]{7,10}',a.mssv): parser.error('MSSV phai co 7-10 chu so.')
    target=Path(a.out);target.mkdir(parents=True,exist_ok=True)
    sol=target/'AuditTarget.sol'; identity=target/'lab_identity.json'
    if (sol.exists() or identity.exists()) and not a.force:
        parser.error('Da co target/identity. Dung thu muc moi; khong ghi de bai da sua (chi --force khi chac chan).')
    source, contract=generate(a.mssv)
    session = 'SC-'+secrets.token_hex(3).upper()
    info = {'mssv':a.mssv, 'session_code':session, 'contract':contract,
            'baseline_sha256':hashlib.sha256(source.encode('utf-8')).hexdigest(),
            'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'solidity':'0.8.24', 'note':'session_code sinh tai may SV, KHONG do GV cap'}
    sol.write_text(source,encoding='utf-8',newline='\n')
    identity.write_text(json.dumps(info,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('DA TAO:',sol,'| Contract:',contract,'| Session:',session)
    print('Khong chay lai voi --force sau khi bat dau sua AuditTarget.sol!')
if __name__ == '__main__': main()
