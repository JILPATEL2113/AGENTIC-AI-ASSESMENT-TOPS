"""
Section B - Task 4: Multi-Agent Order Lifecycle System
Assessment: M20-A1 (Data Science - Modules 19-20)

Coordinator OrderAgent -> DispatchAgent -> SupportAgent ko chain karta hai
aur pura order lifecycle ka report print karta hai.
"""

import time
import random


class OrderAgent:
    def process(self, data):
        # data: raw customer input dict {customer_name, item, quantity, restaurant}
        order_summary = {
            "customer_name": data["customer_name"],
            "item": data["item"],
            "quantity": data["quantity"],
            "restaurant": data["restaurant"],
            "order_id": f"ORD{random.randint(1000, 9999)}",
        }
        return order_summary


class DispatchAgent:
    PARTNERS = ["Ravi K.", "Sneha P.", "Amit D.", "Fatima S."]

    def process(self, data):
        # data: order_summary from OrderAgent
        partner = random.choice(self.PARTNERS)
        eta_minutes = random.randint(20, 45)
        dispatch_details = {
            "order_id": data["order_id"],
            "delivery_partner": partner,
            "eta_minutes": eta_minutes,
        }
        return dispatch_details


class SupportAgent:
    def process(self, data):
        # data: feedback text (string)
        feedback = data.lower()

        if "great" in feedback or "good" in feedback or "on time" in feedback or "thank" in feedback:
            classification = "positive"
            technique = "prompt"
        elif "escalate" in feedback or "refund" in feedback or "manager" in feedback:
            classification = "escalate"
            technique = "fine_tuned"
        else:
            classification = "complaint"
            technique = "rag"

        return {"classification": classification, "technique_selected": technique}


class Coordinator:
    def __init__(self):
        self.order_agent = OrderAgent()
        self.dispatch_agent = DispatchAgent()
        self.support_agent = SupportAgent()

    def run_lifecycle(self, customer_input, feedback):
        start = time.time()

        order_summary = self.order_agent.process(customer_input)
        dispatch_details = self.dispatch_agent.process(order_summary)
        support_result = self.support_agent.process(feedback)

        total_time = round(time.time() - start, 4)

        report = {
            "order_summary": order_summary,
            "dispatch_details": dispatch_details,
            "feedback_classification": support_result["classification"],
            "technique_selected": support_result["technique_selected"],
            "total_simulated_processing_time_sec": total_time,
        }

        self._print_report(report)
        return report

    @staticmethod
    def _print_report(report):
        print("\n----- LIFECYCLE REPORT -----")
        print(f"Order Summary       : {report['order_summary']}")
        print(f"Dispatch Details    : {report['dispatch_details']}")
        print(f"Feedback Classified : {report['feedback_classification']}")
        print(f"Technique Selected  : {report['technique_selected']}")
        print(f"Total Time (sec)    : {report['total_simulated_processing_time_sec']}")
        print("-----------------------------")


if __name__ == "__main__":
    coordinator = Coordinator()

    # Scenario 1: smooth delivery
    print("=== Scenario 1: Smooth Delivery ===")
    coordinator.run_lifecycle(
        customer_input={
            "customer_name": "Priya Shah",
            "item": "Masala Dosa",
            "quantity": 2,
            "restaurant": "Saravana Bhavan",
        },
        feedback="Food was great and delivered on time, thank you!",
    )

    # Scenario 2: complaint
    print("\n=== Scenario 2: Complaint Scenario ===")
    coordinator.run_lifecycle(
        customer_input={
            "customer_name": "Rahul Mehta",
            "item": "Paneer Butter Masala",
            "quantity": 1,
            "restaurant": "Punjabi Tadka",
        },
        feedback="This is unacceptable, please escalate to a manager, I want a refund.",
    )
