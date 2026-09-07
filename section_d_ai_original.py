"""
Section D - Step 1: AI's ORIGINAL solution (as generated, with a bug left in intentionally
to demonstrate the required debugging step).

Prompt given to the AI tool (verbatim, see section_d_prompts.txt):
"Write a Python program that implements a simplified ReAct (Reason + Action) loop for a
food delivery customer support agent that processes a user complaint query. It should run
at least two Reason-Action-Observation cycles, print each cycle's thought/action/observation,
call at least two tool functions (lookup_order_status(order_id) and
check_refund_eligibility(order_id)), and handle the case where a tool returns an error or
'not found' result without crashing."
"""

# ---- Tool functions ----

def lookup_order_status(order_id):
    orders = {
        "FD1001": "delivered",
        "FD1002": "in_transit",
    }
    return orders[order_id]  # BUG: raises KeyError if order_id not found, crashes the program


def check_refund_eligibility(order_id):
    eligible_orders = {"FD1001": True, "FD1002": False}
    return eligible_orders[order_id]  # BUG: same issue, no .get() with default


def react_agent(order_id, complaint):
    print(f"User complaint: {complaint} (Order: {order_id})\n")

    # Cycle 1
    print("Cycle 1")
    print(f"Thought: I need to check the status of order {order_id} first.")
    status = lookup_order_status(order_id)
    print(f"Action: lookup_order_status('{order_id}')")
    print(f"Observation: order status = {status}\n")

    # Cycle 2
    print("Cycle 2")
    print(f"Thought: Now I need to check if this order is eligible for a refund.")
    eligible = check_refund_eligibility(order_id)
    print(f"Action: check_refund_eligibility('{order_id}')")
    print(f"Observation: refund eligible = {eligible}\n")

    if eligible:
        print("Final response: Your refund has been approved.")
    else:
        print("Final response: This order is not eligible for a refund, offering a discount instead.")


if __name__ == "__main__":
    react_agent("FD1001", "My food arrived cold")
    print("\n---\n")
    react_agent("FD9999", "Order never arrived")  # This crashes with KeyError
