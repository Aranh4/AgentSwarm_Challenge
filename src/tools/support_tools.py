"""
Customer Support Tools
Exposes database functions as CrewAI tools.
"""

from crewai.tools import tool
from src.db.client import db_client
from src.utils.session_manager import session_manager

@tool("get_user_info")
def get_user_info_tool(user_id: str) -> str:
    """
    Get customer's personal info and account status.
    
    Args:
        user_id: Check the user_id provided in the context.
    
    Returns:
        String detailing name, balance, status and any block reason.
    """
    user = db_client.get_user(user_id)
    if not user:
        return f"User ID '{user_id}' not found in the system."
    
    # Cache user data in session for future requests
    session_manager.update_session(user_id, {
        "name": user['name'],
        "balance": user['balance'],
        "account_status": user['account_status']
    })
    
    status_info = f"Status: {user['account_status'].upper()}"
    if user['account_status'] == 'blocked':
        status_info += f" (Reason: {user['block_reason']})"
        
    result = f"""
    User Info:
    - Name: {user['name']}
    - Balance: R$ {user['balance']:.2f}
    - {status_info}
    """
    
    from src.utils.debug_tracker import log_tool_usage
    log_tool_usage(
        tool_name="DB: Get User Info",
        input_str=user_id,
        output_str=result,
        metadata={"user_found": True, "status": user['account_status']}
    )
    
    return result

@tool("get_user_transactions")
def get_user_transactions_tool(user_id: str) -> str:
    """
    Get list of recent transactions for the user.
    Useful for checking transfers, pix, payments history.
    
    Args:
        user_id: The customer ID.
        
    Returns:
        List of last 5 transactions with status and details.
    """
    txs = db_client.get_transactions(user_id)
    
    if not txs:
        result = "No recent transactions found."
    else:
        tx_list = []
        for tx in txs:
            tx_str = f"- [{tx['created_at']}] {tx['type'].upper()}: R$ {tx['amount']:.2f} ({tx['status']})"
            
            if tx['status'] == 'failed':
                reason = tx.get('failure_reason', 'Unknown')
                tx_str += f" | Reason: {reason}"
                
            counterparty = tx.get('counterparty')
            if counterparty:
                tx_str += f" | To/From: {counterparty}"
                
            tx_list.append(tx_str)
        result = "\n".join(tx_list)

    from src.utils.debug_tracker import log_tool_usage
    log_tool_usage(
        tool_name="DB: Get Transactions",
        input_str=user_id,
        output_str=result,
        metadata={"count": len(txs) if txs else 0}
    )
        
    return result

@tool("get_user_cards")
def get_user_cards_tool(user_id: str) -> str:
    """
    Get details of user's registered cards.
    Useful for questions about credit limit or card status.
    
    Args:
        user_id: The customer ID.
        
    Returns:
        List of cards with limits and status.
    """
    cards = db_client.get_cards(user_id)
    
    if not cards:
        result = "No cards registered for this user."
    else:
        card_list = []
        for card in cards:
            card_str = (
                f"- Card *{card['last_4']} ({card['status'].upper()})\n"
                f"  Limit: R$ {card['limit_amount']:.2f}\n"
                f"  Used: R$ {card['used_amount']:.2f}\n"
                f"  Available: R$ {card['limit_amount'] - card['used_amount']:.2f}"
            )
            card_list.append(card_str)
        result = "\n".join(card_list)

    from src.utils.debug_tracker import log_tool_usage
    log_tool_usage(
        tool_name="DB: Get Cards",
        input_str=user_id,
        output_str=result,
        metadata={"count": len(cards) if cards else 0}
    )
        
    return result
