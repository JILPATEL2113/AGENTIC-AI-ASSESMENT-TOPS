"""
Section C - Mini Capstone: Agentic Food Delivery Assistant
Assessment: M20-A1 (Data Science - Modules 19-20)

Menu-driven console agent jo tool-calling + memory + strategy selection
sabko integrate karta hai. NOTE: interactive input() ke bajaye ek
auto-run demo mode diya hai (SIMULATED_INPUTS list) taaki bina manual
typing ke pura flow test/screenshot ho sake. Manual run ke liye
RUN_INTERACTIVE = True kar dena.
"""

import random

RUN_INTERACTIVE = False  # True karne par real input() se chalega

# ---------- Tool functions ----------

def place_order(item, restaurant):
    order_id = f"ORD{random.randint(1000,9999)}"
    return order_id, f"Order placed: {item} from {restaurant}. Order ID: {order_id}"


def track_order(order_id):
    eta = random.randint(15, 45)
    return f"Order {order_id} is on the way. ETA: {eta} minutes."


def file_complaint(order_id, issue):
    ticket = f"CMP-{random.randint(100,999)}"
    return f"Complaint logged for order {order_id} ('{issue}'). Ticket: {ticket}"


def get_recommendations(preferred_cuisine):
    cuisine = preferred_cuisine or "popular"
    return f"Based on your preferences, we recommend top {cuisine} dishes near you."


TOOL_SCHEMAS = [
    {"name": "place_order", "description": "Place a new food order.",
     "parameters": {"item": "string", "restaurant": "string"}},
    {"name": "track_order", "description": "Track the status of an existing order.",
     "parameters": {"order_id": "string"}},
    {"name": "file_complaint", "description": "File a complaint against an order.",
     "parameters": {"order_id": "string", "issue": "string"}},
    {"name": "get_recommendations", "description": "Get personalised dish recommendations.",
     "parameters": {"preferred_cuisine": "string"}},
]


def decide_response_strategy(action_type, memory):
    """Pick prompt / rag / fine_tuned based on action type + memory state."""
    if action_type == "file_complaint" and memory["complaints_filed"] >= 2:
        return "fine_tuned"
    if action_type in ("track_order", "get_recommendations"):
        return "rag"
    return "prompt"


class AgenticFoodDeliveryAssistant:
    def __init__(self):
        self.session_memory = {
            "orders_placed": 0,
            "complaints_filed": 0,
            "preferred_cuisine": None,
            "interaction_count": 0,
        }
        self.session_log = []  # list of dicts: action, tool, args, result, strategy
        self.last_order_id = None

    def _log_action(self, action, tool, args, result, strategy):
        self.session_memory["interaction_count"] += 1
        self.session_log.append({
            "action": action, "tool": tool, "args": args,
            "result": result, "strategy": strategy,
        })

    def do_place_order(self, item, restaurant, cuisine=None):
        order_id, result = place_order(item, restaurant)
        self.last_order_id = order_id
        self.session_memory["orders_placed"] += 1
        if cuisine:
            self.session_memory["preferred_cuisine"] = cuisine
        strategy = decide_response_strategy("place_order", self.session_memory)
        self._log_action("Place Order", "place_order", {"item": item, "restaurant": restaurant}, result, strategy)
        print(f"[{strategy}] {result}")

    def do_track_order(self, order_id=None):
        order_id = order_id or self.last_order_id or "UNKNOWN"
        result = track_order(order_id)
        strategy = decide_response_strategy("track_order", self.session_memory)
        self._log_action("Track Order", "track_order", {"order_id": order_id}, result, strategy)
        print(f"[{strategy}] {result}")

    def do_file_complaint(self, issue, order_id=None):
        order_id = order_id or self.last_order_id or "UNKNOWN"
        self.session_memory["complaints_filed"] += 1
        result = file_complaint(order_id, issue)
        strategy = decide_response_strategy("file_complaint", self.session_memory)
        self._log_action("File Complaint", "file_complaint", {"order_id": order_id, "issue": issue}, result, strategy)
        print(f"[{strategy}] {result}")

    def do_get_recommendations(self):
        result = get_recommendations(self.session_memory["preferred_cuisine"])
        strategy = decide_response_strategy("get_recommendations", self.session_memory)
        self._log_action("Get Recommendations", "get_recommendations",
                          {"preferred_cuisine": self.session_memory["preferred_cuisine"]}, result, strategy)
        print(f"[{strategy}] {result}")

    def print_session_report(self):
        print("\n===== SESSION REPORT =====")
        for i, entry in enumerate(self.session_log, start=1):
            print(f"{i}. Action: {entry['action']} | Tool: {entry['tool']} | "
                  f"Args: {entry['args']} | Strategy: {entry['strategy']} | Result: {entry['result']}")
        print(f"\nFinal session_memory: {self.session_memory}")
        print("===========================")


def run_demo():
    assistant = AgenticFoodDeliveryAssistant()

    print("=== MCP-style Tool Schemas (printed once at start) ===")
    for schema in TOOL_SCHEMAS:
        print(schema)

    print("\n=== Menu-driven simulation ===")
    print("(1) Place Order  (2) Track Order  (3) File Complaint  (4) Get Recommendations  (5) Exit\n")

    # Simulated sequence of menu choices to demonstrate the full flow end-to-end
    assistant.do_place_order(item="Masala Dosa", restaurant="Saravana Bhavan", cuisine="south indian")
    assistant.do_track_order()
    assistant.do_file_complaint(issue="Food arrived cold")
    assistant.do_file_complaint(issue="Order was 30 minutes late")  # 2nd complaint -> triggers fine_tuned
    assistant.do_get_recommendations()

    assistant.print_session_report()


def run_interactive():
    assistant = AgenticFoodDeliveryAssistant()
    print("=== MCP-style Tool Schemas (printed once at start) ===")
    for schema in TOOL_SCHEMAS:
        print(schema)

    while True:
        print("\n(1) Place Order  (2) Track Order  (3) File Complaint  (4) Get Recommendations  (5) Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            item = input("Item name: ")
            restaurant = input("Restaurant: ")
            cuisine = input("Cuisine (optional): ") or None
            assistant.do_place_order(item, restaurant, cuisine)
        elif choice == "2":
            order_id = input("Order ID (blank = last order): ") or None
            assistant.do_track_order(order_id)
        elif choice == "3":
            issue = input("Describe the issue: ")
            order_id = input("Order ID (blank = last order): ") or None
            assistant.do_file_complaint(issue, order_id)
        elif choice == "4":
            assistant.do_get_recommendations()
        elif choice == "5":
            assistant.print_session_report()
            break
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    if RUN_INTERACTIVE:
        run_interactive()
    else:
        run_demo()
