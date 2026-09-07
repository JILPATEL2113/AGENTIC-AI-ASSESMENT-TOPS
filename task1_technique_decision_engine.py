"""
Section B - Task 1: AI Technique Decision Engine
Assessment: M20-A1 (Data Science - Modules 19-20)

Function recommends Prompt Engineering / RAG / Fine-Tuning based on
4 structured inputs, using a rule-based decision tree.
"""


def recommend_technique(update_frequency, data_in_external_docs, needs_custom_behaviour, latency_budget):
    """
    update_frequency        : 'high' / 'low'  -> kitna fast data change hota hai
    data_in_external_docs   : 'yes' / 'no'    -> answer external docs/db me hai kya
    needs_custom_behaviour  : 'yes' / 'no'    -> model ka tone/style/format customize karna hai kya
    latency_budget          : 'low' / 'high'  -> response fast chahiye (low budget) ya thoda slow chalega
    """
    update_frequency = update_frequency.lower()
    data_in_external_docs = data_in_external_docs.lower()
    needs_custom_behaviour = needs_custom_behaviour.lower()
    latency_budget = latency_budget.lower()

    # Rule 1: Data fast-changing + external docs available -> RAG hi best hai
    if update_frequency == "high" and data_in_external_docs == "yes":
        technique = "RAG"
        justification = (
            "Data changes frequently, so baking it into model weights via fine-tuning would go stale immediately. "
            "Since the facts already live in external docs/DB, retrieval at query time keeps answers current without retraining."
        )

    # Rule 2: Static custom behaviour needed, data doesn't change, no external doc dependency -> Fine-Tuning
    elif needs_custom_behaviour == "yes" and update_frequency == "low" and data_in_external_docs == "no":
        technique = "Fine-Tuning"
        justification = (
            "The task needs a consistent custom behaviour/style baked into the model, and the underlying knowledge is stable. "
            "Fine-tuning permanently encodes this behaviour, avoiding the need to repeat lengthy instructions every call."
        )

    # Rule 3: Low latency budget + no external doc dependency + no heavy custom behaviour -> Prompt Engineering
    elif latency_budget == "low" and data_in_external_docs == "no" and needs_custom_behaviour == "no":
        technique = "Prompt Engineering"
        justification = (
            "There is no external knowledge dependency and no deep behavioural customization needed, only fast responses. "
            "A well-crafted prompt is the cheapest and fastest option, avoiding both retrieval and training overhead."
        )

    # Rule 4: External docs available but data doesn't change often + custom behaviour also needed -> RAG + Fine-Tuning combo (favor RAG as primary)
    elif data_in_external_docs == "yes" and needs_custom_behaviour == "yes":
        technique = "RAG"
        justification = (
            "External documents hold the factual grounding needed, which RAG retrieves reliably regardless of update frequency. "
            "Custom behaviour/style can be layered on top via prompt instructions, avoiding costly fine-tuning for a data problem."
        )

    # Rule 5: High latency budget (can tolerate slower calls) + custom behaviour + no external doc need -> Fine-Tuning
    elif latency_budget == "high" and needs_custom_behaviour == "yes" and data_in_external_docs == "no":
        technique = "Fine-Tuning"
        justification = (
            "With a tolerant latency budget and a genuine need for consistent custom behaviour not tied to external facts, "
            "fine-tuning is worth the training investment since it removes repeated prompt overhead at inference time."
        )

    # Default fallback rule
    else:
        technique = "Prompt Engineering"
        justification = (
            "None of the stronger conditions for RAG or Fine-Tuning are met based on the given inputs. "
            "Prompt Engineering is the safest low-cost default until a clearer need for retrieval or training emerges."
        )

    return {"technique": technique, "justification": justification}


if __name__ == "__main__":
    scenarios = [
        {
            "name": "Real-time menu recommendations",
            "args": dict(update_frequency="high", data_in_external_docs="yes",
                         needs_custom_behaviour="no", latency_budget="low"),
        },
        {
            "name": "Complaint categorisation",
            "args": dict(update_frequency="low", data_in_external_docs="no",
                         needs_custom_behaviour="yes", latency_budget="high"),
        },
        {
            "name": "Order confirmation message generation",
            "args": dict(update_frequency="low", data_in_external_docs="no",
                         needs_custom_behaviour="no", latency_budget="low"),
        },
        {
            "name": "Domain-specific FAQ answering",
            "args": dict(update_frequency="low", data_in_external_docs="yes",
                         needs_custom_behaviour="yes", latency_budget="high"),
        },
    ]

    for scenario in scenarios:
        result = recommend_technique(**scenario["args"])
        print(f"\nScenario: {scenario['name']}")
        print(f"  Inputs        : {scenario['args']}")
        print(f"  Technique     : {result['technique']}")
        print(f"  Justification : {result['justification']}")
