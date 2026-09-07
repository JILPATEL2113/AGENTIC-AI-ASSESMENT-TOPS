"""
Section B - Task 3: Memory-Aware Strategy Selector
Assessment: M20-A1 (Data Science - Modules 19-20)

Per-user memory maintain karke, decide karta hai ki response
prompt_template / rag_lookup / fine_tuned se dena hai.
"""


# ---------- Strategy functions ----------

def prompt_template_response(query):
    return f"[Prompt-Template] Thanks for reaching out! Regarding '{query}', here's a quick general answer for you."


def rag_lookup_response(query):
    return f"[RAG-Lookup] Retrieved live menu/item data relevant to '{query}' from the restaurant database."


def fine_tuned_response(query):
    return f"[Fine-Tuned-Model] Based on learned complaint-handling patterns, here is a tailored resolution for: '{query}'."


# ---------- Per-user memory ----------

memory = {}  # user_id -> {interaction_count, preferred_cuisine, last_complaint}


def _ensure_user(user_id):
    if user_id not in memory:
        memory[user_id] = {
            "interaction_count": 0,
            "preferred_cuisine": None,
            "last_complaint": None,
        }


def _update_memory(user_id, query):
    _ensure_user(user_id)
    memory[user_id]["interaction_count"] += 1

    q = query.lower()
    # simple keyword-based cuisine detection
    for cuisine in ["south indian", "north indian", "chinese", "italian", "mexican"]:
        if cuisine in q:
            memory[user_id]["preferred_cuisine"] = cuisine
            break

    if "complaint" in q or "cold" in q or "late" in q or "wrong" in q:
        memory[user_id]["last_complaint"] = query


def decide_strategy(user_id, query):
    """Decide strategy AFTER updating memory for this interaction."""
    _update_memory(user_id, query)
    q = query.lower()
    interactions = memory[user_id]["interaction_count"]

    is_complaint = "complaint" in q or "cold" in q or "late" in q or "wrong" in q
    is_menu_query = "menu" in q or "item" in q or "dish" in q or "available" in q

    if is_complaint and interactions >= 3:
        strategy = "fine_tuned"
        response = fine_tuned_response(query)
    elif is_menu_query:
        strategy = "rag_lookup"
        response = rag_lookup_response(query)
    else:
        strategy = "prompt_template"
        response = prompt_template_response(query)

    return strategy, response


if __name__ == "__main__":
    user_id = "user_101"

    interactions = [
        "Hi, do you have South Indian menu items today?",
        "What Chinese dishes are available?",
        "My order arrived cold, that's a complaint",
        "This is the same complaint as before, order was late again",
        "Complaint: wrong item delivered again",
    ]

    print(f"=== Simulating interactions for {user_id} ===")
    for i, query in enumerate(interactions, start=1):
        strategy, response = decide_strategy(user_id, query)
        print(f"\nInteraction {i}: '{query}'")
        print(f"  Strategy chosen : {strategy}")
        print(f"  Response        : {response}")
        print(f"  Memory state    : {memory[user_id]}")
