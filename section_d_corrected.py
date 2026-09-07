"""
Section D - Step 2: CORRECTED version (bug fixed manually, without AI help).

Bug found: lookup_order_status() and check_refund_eligibility() used dict[key]
indexing, which raises an unhandled KeyError and crashes the whole program when
an order_id isn't found -- exactly the 'not found' case the assignment requires
to be handled gracefully. Fixed by using dict.get() with a safe default, and by
having react_agent() branch its reasoning based on that 'not_found' observation
instead of assuming a valid status always comes back.
"""


def lookup_order_status(order_id):
    orders = {
        "FD1001": "delivered",
        "FD1002": "in_transit",
    }
    return orders.get(order_id, "not_found")  # FIX: safe default instead of raising KeyError


def check_refund_eligibility(order_id):
    eligible_orders = {"FD1001": True, "FD1002": False}
    return eligible_orders.get(order_id, "unknown")  # FIX: safe default


def react_agent(order_id, complaint):
    print(f"User complaint: {complaint} (Order: {order_id})\n")

    # Cycle 1
    print("Cycle 1")
    print(f"Thought: I need to check the status of order {order_id} first.")
    status = lookup_order_status(order_id)
    print(f"Action: lookup_order_status('{order_id}')")
    print(f"Observation: order status = {status}\n")

    if status == "not_found":
        # FIX: incorporate the error observation into the next reasoning step,
        # instead of blindly proceeding to check refund eligibility on bad data.
        print("Cycle 2")
        print("Thought: The order ID could not be found, so I cannot check refund "
              "eligibility for a non-existent order. I should ask the user to verify the order ID.")
        print("Action: none (skipping check_refund_eligibility)")
        print("Observation: order_id invalid, cannot proceed further.\n")
        print("Final response: We couldn't find that order. Could you please double-check "
              "the order ID and try again?")
        return

    # Cycle 2 (only reached if the order was actually found)
    print("Cycle 2")
    print("Thought: Now I need to check if this order is eligible for a refund.")
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
    react_agent("FD9999", "Order never arrived")  # No longer crashes - handled gracefully
