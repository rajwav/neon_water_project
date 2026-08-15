# NEON Water Intelligence Platform — SHAP Explainable AI Documentation

**Document**: XAI SHAP Technical Specification & Environmental Attribution Guide  
**Module**: `src/ml/xai_explainer.py`  
**Integration**: Backend (`backend/main.py`, `backend/model_loader.py`) & Frontend (`dashboard/app.py`)  
**Version**: 5.0.0  

---

## 1. Executive Summary

In high-stakes environmental monitoring and municipal water security, black-box artificial intelligence models are unacceptable to water resource authorities, treatment plant operators, and environmental regulators. When an AI classifies a river segment as **`CRITICAL`** or **`WARNING`**, operators must understand:

1. **Which specific sensor parameters drove this classification?**
2. **How much did each parameter contribute toward or away from the risk state?**
3. **What is the physical and biogeochemical justification behind the algorithmic output?**

To address this challenge, the NEON Water Intelligence Platform incorporates **SHAP (SHapley Additive exPlanations)** based local feature attribution for Model 2 (Operational Risk Classifier). Every prediction returned by the `/predict` API includes a dedicated `xai_explanation` payload detailing quantitative SHAP values, risk directionality, parameter baseline assessments, and natural language diagnostic summaries.

---

## 2. What is SHAP?

**SHAP (SHapley Additive exPlanations)** is a game-theoretic approach to explain the output of any machine learning model. Derived from cooperative game theory (Lloyd Shapley, 1953), Shapley values distribute the "payout" (the model's prediction score) fairly among all "players" (the input features).

### Core Mathematical Properties of SHAP

1. **Efficiency / Local Accuracy**: The sum of feature Shapley values plus the expected base rate equals the model prediction:
   $$\sum_{i=1}^{M} \phi_i(x) + \phi_0 = f(x)$$
   Where:
   - $f(x)$ is the model output probability for sample $x$.
   - $\phi_0 = \mathbb{E}[f(z)]$ is the expected baseline prediction across the dataset.
   - $\phi_i(x)$ is the Shapley attribution value for feature $i$.

2. **Symmetry (Equal Contribution)**: If two features $i$ and $j$ contribute equally to all possible feature subsets, their SHAP values are identical:
   $$\phi_i(x) = \phi_j(x)$$

3. **Dummy / Null Feature**: If feature $i$ has no impact on model predictions across all coalitions, its SHAP value is exactly zero:
   $$\phi_i(x) = 0$$

4. **Additivity**: For an ensemble model $f(x) = \sum_k w_k f_k(x)$, the total SHAP value is the weighted sum of individual trees' SHAP values:
   $$\phi_i(f) = \sum_k w_k \phi_i(f_k)$$

---

## 3. Why Use SHAP for Environmental AI?

Traditional feature importance methods (such as Gini impurity decrease or permutation importance) provide only **global** insights—they tell you which parameters were important across the entire training dataset on average. However, they fail to answer **local** questions for an individual water sample in real time.

| Evaluation Dimension | Global Feature Importance (Gini) | Local SHAP Attribution |
|---|---|---|
| **Scope** | Dataset-wide average | Exact per-sample explanation |
| **Directionality** | Magnitude only (always positive) | Signed (+ increases risk, - protects safety) |
| **Real-Time Utility** | Offline analysis only | Online per-inference telemetry diagnostics |
| **Operational Guidance** | Cannot guide specific incident response | Directly identifies which valve/probe to inspect |
| **Consistency** | Sensitive to feature correlations | Mathematically guaranteed consistency |

---

## 4. How TreeExplainer Works

Our implementation uses **TreeExplainer**, a polynomial-time algorithm optimized for tree-based ensemble models (Random Forests, Gradient Boosted Trees):

### Step-by-Step Tree Decision Path Decomposition

1. **Path Traversal**: For an input feature vector $x$, the explainer identifies the decision path taken across every individual decision tree $t \in \{1, \dots, T\}$ in the ensemble.
2. **Conditional Expectation Shift**: At each internal node $n$ on the decision path splitting on feature $k$, the explainer computes the change in class probability between the parent node and the child node:
   $$\Delta P_k^{(t)} = P(\text{Class} \mid \text{Child Node}) - P(\text{Class} \mid \text{Parent Node})$$
3. **Ensemble Aggregation**: The individual tree contributions are averaged across the complete forest:
   $$\phi_k(x) = \frac{1}{T} \sum_{t=1}^{T} \Delta P_k^{(t)}$$
4. **Directional Mapping**:
   - **$\phi_k > 0$**: Feature $k$ pushes the prediction **toward** the predicted operational risk state.
   - **$\phi_k < 0$**: Feature $k$ pulls the prediction **away** from the risk state (protective effect).
   - **$\phi_k \approx 0$**: Feature $k$ has negligible influence on this specific prediction.

---

## 5. System Integration & Data Flow

```
   Raw Sensor Telemetry (pH, DO, Turbidity, Conductance, Nutrients, Bio)
                                  │
                                  ▼
           ┌──────────────────────────────────────────────┐
           │        Model 2: Balanced Random Forest       │
           │      (models/v3/risk_classifier_usgs)        │
           └──────────────────────┬───────────────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
      Operational Risk Prediction         SHAP TreeExplainer
      (SAFE / WARNING / CRITICAL)    (src/ml/xai_explainer.py)
                  │                               │
                  │   Decision Path Decomposition │
                  │   Per-Feature Shapley Values  │
                  │                               ▼
                  │                   ┌───────────────────────┐
                  │                   │  Top Impact Drivers   │
                  │                   │  Natural Language XAI │
                  │                   └───────────┬───────────┘
                  │                               │
                  └───────────────┬───────────────┘
                                  ▼
                     FastAPI /predict Endpoint
                    (backend/model_loader.py)
                                  │
                                  ▼
               Structured JSON Response (`xai_explanation`)
                                  │
                                  ▼
                Streamlit Operations Console (Tab 1)
              "Why AI Reached This Decision" UI Block
             • Horizontal SHAP Impact Bar Chart
             • Full Feature Attribution Breakdown Table
```

---

## 6. Example API Output Schema

```json
{
  "prediction": "CRITICAL",
  "prediction_reason": "Critical risk mainly caused by abnormal turbidity (150.0 FNU) and dissolved oxygen (1.5 mg/L).",
  "top_features": [
    {
      "feature": "Turbidity (FNU)",
      "value": "150.0",
      "impact": "+0.4671",
      "direction": "increase risk"
    },
    {
      "feature": "Dissolved Oxygen (mg/L)",
      "value": "1.5",
      "impact": "+0.1851",
      "direction": "increase risk"
    },
    {
      "feature": "Water pH",
      "value": "2.8",
      "impact": "+0.0915",
      "direction": "increase risk"
    }
  ],
  "feature_contributions": [
    {
      "feature": "turbidity_fnu",
      "label": "Turbidity (FNU)",
      "value": "150.0",
      "raw_value": 150.0,
      "impact": 0.4671,
      "abs_impact": 0.4671,
      "direction": "increase risk",
      "value_assessment": "above safe range (25.0)"
    },
    {
      "feature": "dissolved_oxygen_mg_l",
      "label": "Dissolved Oxygen (mg/L)",
      "value": "1.5",
      "raw_value": 1.5,
      "impact": 0.1851,
      "abs_impact": 0.1851,
      "direction": "increase risk",
      "value_assessment": "below safe range (6.0)"
    }
  ]
}
```

---

## 7. Why Explainability Matters in Environmental AI

1. **Regulatory Defensibility**: Environmental protection agencies (CPCB, US EPA) require legally defensible evidence before issuing industrial shutdown notices or containment orders.
2. **False Alarm Mitigation**: Operators can immediately verify whether an alert was triggered by a real environmental hazard or an isolated sensor calibration artifact.
3. **Targeted Field Remediation**: Knowing that high phosphorus ($\phi = +0.32$) rather than industrial metals triggered a warning allows authorities to inspect agricultural drainage channels rather than chemical plants.
4. **Human-in-the-Loop Governance**: Combines machine learning speed (<15ms) with domain expert accountability.
