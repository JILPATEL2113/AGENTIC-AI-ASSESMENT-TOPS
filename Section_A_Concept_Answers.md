# Section A — Concept Application
**Assessment Code: M20-A1 | Data Science | Modules 19–20**

---

### S1. Prompt Engineering vs RAG vs Fine-Tuning (Dish Recommendation Chatbot)

**Prompt Engineering alone** falls short here because the chatbot needs *real-time menu availability* — a static prompt cannot encode data that changes every few minutes across thousands of restaurants. It's cheap and fast to set up but has no memory of facts outside the prompt window.

**Fine-tuning** falls short too. Fine-tuning bakes knowledge into model weights at training time — it cannot reflect menu changes that happen daily without constant retraining, which is slow and expensive. It's suited to teaching *behaviour/style*, not fast-changing facts.

**RAG (Retrieval-Augmented Generation)** is the right fit for the *menu/order-history* part, because it retrieves live data (menu availability, past orders, dietary tags) from a database/vector store at query time — so it's always current with zero retraining cost.

**Recommendation:** Use **RAG + light Prompt Engineering** as a combination:
- RAG retrieves the user's dietary restrictions, order history, and current restaurant menu.
- Prompt engineering (a well-structured system prompt) tells the model *how* to reason over that retrieved context and format the recommendation.
- Fine-tuning is not justified here — the problem is a data-freshness problem, not a behaviour/style problem, and the cost/latency of retraining daily is not worth it.

---

### S2. LoRA (Low-Rank Adaptation) Under 8GB VRAM

**What LoRA modifies:** Instead of updating all the original weight matrices of the pre-trained model (which for a 7B model means billions of parameters), LoRA freezes the original weights entirely and injects small trainable **low-rank decomposition matrices** (A and B, where the update ΔW ≈ A·B) alongside specific layers (typically attention projection layers). Only these small matrices are trained.

**Why it's viable under VRAM constraints:** Because the base model stays frozen, you don't need to store optimizer states (momentum, variance, gradients) for billions of parameters — only for the tiny LoRA matrices (often <1% of total parameters). This cuts VRAM needs from potentially 80GB+ (full fine-tuning of a 7B model with Adam optimizer) down to a level that fits on an 8GB consumer GPU, especially when combined with quantization (QLoRA).

**Trade-off accepted:** LoRA has slightly less expressive capacity than full fine-tuning since it only learns a low-rank approximation of the ideal weight update. For most domain-adaptation tasks (like food-service customer queries) this gap is negligible, but for very large behavioural shifts or tasks requiring deep architectural change, full fine-tuning may still outperform LoRA. There's also a small inference-time cost if the LoRA adapter isn't merged into the base weights (extra matrix multiply), though this is usually solved by merging after training.

---

### S3. Fine-Tuning Limitations Exposed by the Complaint Classifier

**Limitation 1 — Poor generalisation to out-of-distribution (rare) inputs.**
A model fine-tuned on 6,000 labelled tickets learns the *statistical patterns* of what it has seen. Complaints with no representation in training data (e.g., a culturally/contextually specific complaint like "rude during a religious event") fall outside the learned distribution, so the model has no reliable basis to classify them.
- **Best remedy: Few-shot prompting in the system prompt.**
- **Condition under which it's valid:** This works well when the rare case is *infrequent* (doesn't justify a full retraining cycle) and can be described with a handful of illustrative examples added to the prompt at inference time — cheap and immediate, no retraining needed.

**Limitation 2 — Static/frozen knowledge (the model can't incorporate new complaint categories as they emerge).**
Fine-tuning only reflects the snapshot of data available *at training time*. As new complaint types emerge over time (seasonal events, new city-specific issues), the classifier goes stale.
- **Best remedy: Switching to RAG** — retrieve similar historical complaint resolutions/examples at inference time from a continuously updated knowledge base, so new patterns can be incorporated without retraining.
- **Condition under which it's valid:** This works when there is a growing, retrievable corpus of past complaints/resolutions to search over, and when the categorisation logic can be inferred from similar retrieved examples rather than needing deeply learned decision boundaries.

*(Re-fine-tuning with more data is only the right remedy when the rare cases become frequent enough — e.g. accumulate hundreds of similar tickets — that it's worth the cost of a retraining cycle to bake the pattern into the weights permanently.)*

---

### S4. Perceive → Think → Act Loop (Order Agent)

**Perceive:**
The agent parses the raw message *"Order 2 portions of Masala Dosa from Saravana Bhavan for delivery at 7 PM tonight"* and extracts structured entities:
- item = "Masala Dosa", quantity = 2
- restaurant = "Saravana Bhavan"
- delivery_time = "7:00 PM today"

**Think:**
The agent reasons about ambiguities before acting:
- Which "Saravana Bhavan" branch (if multiple exist near the user)? → needs disambiguation, defaults to nearest branch or asks the user.
- Is "tonight" today's date, and is 7 PM still in the future relative to current time?
- Does the item exist on that restaurant's current menu?
It plans a tool-call sequence: first verify restaurant/menu availability, *then* estimate delivery feasibility, *then* place the order — because placing the order before verifying availability could fail mid-transaction.

**Act:**
Tool calls in order:
1. `check_restaurant_status("Saravana Bhavan")` — confirm open & item available at 7 PM.
2. `get_estimated_delivery_time(...)` — confirm 7 PM slot is achievable.
3. `place_order(...)` — only if steps 1–2 succeed.

**If Saravana Bhavan is unavailable at 7 PM:** The Act step's observation (tool result) feeds back into a new Think step — the loop doesn't terminate. The agent re-reasons: it can (a) suggest the nearest available time slot at the same restaurant, or (b) suggest an alternative restaurant with the same dish, and then re-perceives the user's response to that suggestion before acting again. This is the essential agentic property — Perceive→Think→Act is a *loop*, not a one-shot pipeline.

---

### S5. Database MCP Server Design

**Tools to expose:**
- `list_tables()` — discover available tables (orders, restaurants, delivery_partners).
- `describe_table(table_name)` — expose schema/column names so the LLM knows what's queryable, without exposing row data.
- `run_select_query(sql)` — execute only `SELECT` statements against the data.

**Access level: Read-only.**
Support/analytics use cases only need to *read* data to answer questions — they never need to modify order/restaurant records. Granting read-write access would let a prompt-injected or hallucinating LLM issue destructive `UPDATE`/`DELETE` statements, so read-only is a critical safety boundary, not just a convenience.

**Example realistic question:** *"Which orders placed in the last 2 hours are still marked 'in transit' and are more than 30 minutes past their estimated delivery time?"* — a support agent would ask this to proactively find delayed orders.

**Safeguard against leaking sensitive data (phone numbers, payment details):**
The MCP server should enforce a **column-level allowlist / view layer** rather than giving `run_select_query` raw access to full tables. For example, expose a SQL **view** (e.g. `orders_support_view`) that already excludes `customer_phone`, `payment_token`, and other PII columns, and only allow queries against that view — not the base tables. Additionally, the server can validate/parse the SQL before execution to reject any query referencing disallowed columns/tables, so even if the LLM's query didn't need sensitive data but might accidentally request `SELECT *`, the view ensures those columns simply don't exist in the queryable surface.

---

### S6. ReAct (Reason + Action) Cycles for a Refund Complaint

**Cycle 1:**
- **Reason (Thought):** "The customer says order #FD4521 was 40 minutes late and arrived cold. Before deciding refund vs discount, I need to verify the actual delivery time and confirm the delay against the promised ETA."
- **Action:** `get_estimated_delivery_time("FD4521")` (or an order-log lookup tool)
- **Observation:** Tool returns: promised ETA = 6:00 PM, actual delivered = 6:42 PM → confirms a 42-minute delay, consistent with the customer's claim.

**Cycle 2:**
- **Reason (Thought):** "The delay is confirmed and matches company policy for delays >30 minutes (which qualifies for compensation). The customer requested either a full refund or a significant discount — policy allows a discount for delays under 45 minutes, a full refund is reserved for delays over 45 minutes or verified food-quality complaints. I should apply a discount and file a note about the cold food."
- **Action:** `apply_discount("FD4521", reason="40-min delay + cold food")`
- **Observation:** Tool returns confirmation: "20% discount code applied to customer's next order."

**Final response:** The agent communicates the discount decision to the customer, citing the verified delay.

**Why separating Reason from Action matters here:** When an agent's actions have *financial consequences* (refunds, discounts), it must not act impulsively on the raw user claim — it must first *verify* facts via tools (Action) and only *then* reason about the correct policy-compliant response. Separating the steps creates an auditable trail (what was reasoned, what was checked, what was observed) and prevents the model from blindly honoring a customer's request without validation — reducing the risk of fraud, inconsistent refund policy application, and unexplainable financial decisions.
