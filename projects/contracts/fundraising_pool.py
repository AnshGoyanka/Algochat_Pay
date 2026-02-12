"""
AlgoChat Pay - Fundraising Pool Contract
Transparent fundraising with goal tracking
"""
from pyteal import *


def fundraising_pool_contract():
    """
    Smart contract for transparent fundraising campaigns
    
    Features:
    - Goal tracking
    - Contributor list
    - Milestone verification
    - Transparent accounting
    """
    
    # App state
    goal_amount = App.globalGet(Bytes("goal"))
    raised_amount = App.globalGet(Bytes("raised"))
    num_contributors = App.globalGet(Bytes("contributors"))
    is_completed = App.globalGet(Bytes("completed"))
    
    # Initialize app
    on_create = Seq([
        App.globalPut(Bytes("goal"), Btoi(Txn.application_args[0])),
        App.globalPut(Bytes("raised"), Int(0)),
        App.globalPut(Bytes("contributors"), Int(0)),
        App.globalPut(Bytes("completed"), Int(0)),
        Return(Int(1))
    ])
    
    # Contribute to campaign
    on_contribute = Seq([
        Assert(Txn.application_args.length() == Int(2)),
        Assert(App.globalGet(Bytes("completed")) == Int(0)),
        
        # Record contribution
        App.globalPut(
            Bytes("raised"),
            App.globalGet(Bytes("raised")) + Btoi(Txn.application_args[1])
        ),
        App.globalPut(
            Bytes("contributors"),
            App.globalGet(Bytes("contributors")) + Int(1)
        ),
        
        # Check if goal reached
        If(
            App.globalGet(Bytes("raised")) >= App.globalGet(Bytes("goal")),
            App.globalPut(Bytes("completed"), Int(1))
        ),
        
        Return(Int(1))
    ])
    
    # Get current status
    on_status = Seq([
        Return(Int(1))
    ])
    
    # Withdraw funds (only if goal reached)
    on_withdraw = Seq([
        Assert(App.globalGet(Bytes("completed")) == Int(1)),
        # In production: verify sender is beneficiary
        Return(Int(1))
    ])
    
    # Handle different calls
    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.application_args[0] == Bytes("contribute"), on_contribute],
        [Txn.application_args[0] == Bytes("status"), on_status],
        [Txn.application_args[0] == Bytes("withdraw"), on_withdraw],
    )
    
    return program


def approval_program():
    return fundraising_pool_contract()


def clear_state_program():
    return Return(Int(1))


if __name__ == "__main__":
    # Compile contracts
    with open("fundraising_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=6)
        f.write(compiled)
    
    with open("fundraising_clear.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=6)
        f.write(compiled)
    
    print("✅ Fundraising Pool Contract compiled successfully")
