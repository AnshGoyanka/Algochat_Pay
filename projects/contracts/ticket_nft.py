"""
AlgoChat Pay - Ticket NFT Contract
Event tickets as verifiable NFTs
"""
from pyteal import *


def ticket_nft_contract():
    """
    Smart contract for NFT-based event tickets
    
    Features:
    - Unique ticket IDs
    - Verification system
    - Anti-scalping controls
    - Resale restrictions
    """
    
    # Initialize app
    on_create = Seq([
        App.globalPut(Bytes("total_tickets"), Btoi(Txn.application_args[0])),
        App.globalPut(Bytes("minted"), Int(0)),
        App.globalPut(Bytes("event_name"), Txn.application_args[1]),
        Return(Int(1))
    ])
    
    # Mint ticket NFT
    on_mint = Seq([
        Assert(App.globalGet(Bytes("minted")) < App.globalGet(Bytes("total_tickets"))),
        
        # Increment counter
        App.globalPut(
            Bytes("minted"),
            App.globalGet(Bytes("minted")) + Int(1)
        ),
        
        # In production: Create ASA with unique metadata
        Return(Int(1))
    ])
    
    # Verify ticket authenticity
    on_verify = Seq([
        # In production: Check ASA ownership and metadata
        Return(Int(1))
    ])
    
    # Transfer ticket (with restrictions)
    on_transfer = Seq([
        # In production: Verify transfer rules
        # - Original buyer can transfer once
        # - Price cap to prevent scalping
        Return(Int(1))
    ])
    
    # Handle different calls
    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.application_args[0] == Bytes("mint"), on_mint],
        [Txn.application_args[0] == Bytes("verify"), on_verify],
        [Txn.application_args[0] == Bytes("transfer"), on_transfer],
    )
    
    return program


def approval_program():
    return ticket_nft_contract()


def clear_state_program():
    return Return(Int(1))


if __name__ == "__main__":
    # Compile contracts
    with open("ticket_nft_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=6)
        f.write(compiled)
    
    with open("ticket_nft_clear.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=6)
        f.write(compiled)
    
    print("✅ Ticket NFT Contract compiled successfully")
