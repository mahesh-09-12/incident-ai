
from app.features.investigation.multi_agent_contracts import (
    MultiAgentInvestigationState,
    RecommendationResult,
    RankedHypothesis,
    MultiAgentHypothesis,
)

def generate_recommendations_node(state: MultiAgentInvestigationState) -> dict:
    ranking = state.get("ranking", [])
    hypotheses = state.get("hypotheses", [])
    
    if not ranking or not hypotheses:
        result = RecommendationResult(
            immediate_mitigations=["No immediate mitigations could be generated."],
            preventative_measures=["No preventative measures could be generated."]
        )
        return {"recommendations": result}

    hyp_map = {h.id: h for h in hypotheses}
    
    # Select the top ranked hypothesis
    top_rank = ranking[0]
    top_hypothesis = hyp_map.get(top_rank.hypothesis_id)
    
    if not top_hypothesis:
        return {"errors": [f"Cannot generate recommendations: Top ranked hypothesis '{top_rank.hypothesis_id}' not found in hypotheses list."]}
        
    result = RecommendationResult(
        immediate_mitigations=top_hypothesis.immediate_mitigations,
        preventative_measures=top_hypothesis.preventative_measures
    )
    
    return {"recommendations": result}
