"""
Section B - Task 2: Tool-Calling Delivery Agent
Assessment: M20-A1 (Data Science - Modules 19-20)

FoodDeliveryAgent class jo customer query ko sahi tool pe route karke
execute karta hai, aur session history log rakhta hai.
"""


# ---------- Tool functions (outside class) ----------

def check_restaurant_status(name):
    # simulate DB lookup
    return f"Restaurant '{name}' is currently OPEN and accepting orders."


def get_estimated_delivery_time(order_id):
    return f"Order {order_id} estimated delivery time: 32 minutes."


def apply_discount(order_id, reason):
    return f"10% discount applied to order {order_id} for reason: '{reason}'."


def file_complaint(order_id, issue):
    return f"Complaint filed for order {order_id}: '{issue}'. Ticket #CMP-{order_id[-4:]} created."


# ---------- MCP-style schemas for each tool ----------

TOOL_SCHEMAS = [
    {
        "name": "check_restaurant_status",
        "description": "Check whether a restaurant is currently open and accepting orders.",
        "parameters": {"name": "string - the restaurant name"},
    },
    {
        "name": "get_estimated_delivery_time",
        "description": "Get the estimated delivery time for a given order id.",
        "parameters": {"order_id": "string - the order identifier"},
    },
    {
        "name": "apply_discount",
        "description": "Apply a discount to an order for a given reason.",
        "parameters": {
            "order_id": "string - the order identifier",
            "reason": "string - reason for the discount",
        },
    },
    {
        "name": "file_complaint",
        "description": "File a complaint against an order with a described issue.",
        "parameters": {
            "order_id": "string - the order identifier",
            "issue": "string - description of the issue",
        },
    },
]


class FoodDeliveryAgent:
    def __init__(self):
        self.session_log = []  # list of (query, tool_called, result) tuples

    def think(self, query):
        """Keyword-based routing -> correct tool + call it."""
        q = query.lower()

        if "open" in q or "status" in q or "available" in q:
            # naive name extraction: text after 'restaurant' keyword, fallback generic
            name = self._extract_after(q, ["restaurant", "at"]) or "the restaurant"
            result = check_restaurant_status(name.title())
            tool_called = "check_restaurant_status"

        elif "eta" in q or "delivery time" in q or "how long" in q:
            order_id = self._extract_order_id(query) or "UNKNOWN"
            result = get_estimated_delivery_time(order_id)
            tool_called = "get_estimated_delivery_time"

        elif "discount" in q or "refund" in q or "compensation" in q:
            order_id = self._extract_order_id(query) or "UNKNOWN"
            result = apply_discount(order_id, reason="customer requested compensation")
            tool_called = "apply_discount"

        elif "complaint" in q or "issue" in q or "problem" in q or "cold" in q or "late" in q:
            order_id = self._extract_order_id(query) or "UNKNOWN"
            result = file_complaint(order_id, issue=query)
            tool_called = "file_complaint"

        else:
            result = "Sorry, I could not map this query to a known tool."
            tool_called = "none"

        self.session_log.append((query, tool_called, result))
        return result

    @staticmethod
    def _extract_order_id(query):
        # order ids ka pattern maan lete hain: '#' ke baad alphanumeric, e.g. #FD4521
        import re
        match = re.search(r"#([A-Za-z0-9]+)", query)
        return match.group(1) if match else None

    @staticmethod
    def _extract_after(text, keywords):
        # restaurant naam nikalne ke liye: "is <name> restaurant" pattern try karo pehle
        import re
        match = re.search(r"is ([a-z ]+?) restaurant", text)
        if match:
            return match.group(1).strip()
        for kw in keywords:
            if kw in text:
                after = text.split(kw, 1)[1].strip()
                word = after.split(" ")[0] if after else None
                return word.strip("?,.") if word else None
        return None


if __name__ == "__main__":
    print("=== MCP-style Tool Schemas ===")
    for schema in TOOL_SCHEMAS:
        print(schema)

    agent = FoodDeliveryAgent()

    test_queries = [
        "Is Saravana Bhavan restaurant open right now?",
        "What is the delivery time for order #FD1234?",
        "My order #FD4521 was cold, I want a discount",
        "I have a complaint about order #FD7788, item was missing",
        "How long will #FD9001 take to arrive?",
    ]

    print("\n=== Test Queries ===")
    for q in test_queries:
        output = agent.think(q)
        print(f"\nQuery : {q}")
        print(f"Result: {output}")

    print("\n=== Session Log ===")
    for entry in agent.session_log:
        print(entry)
