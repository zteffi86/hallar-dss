"""
Hallar Risk Factors Module

Structural approach to risk quantification across development scenarios.

Chain: Structure → Risk Probability → Goal Impact → Weighted Ranking
"""
from .structural_factors import (
    STRUCTURAL_FACTORS,
    SCENARIO_FACTORS,
    StructuralFactor,
    ScenarioFactors,
    get_scenario_profile,
    compare_scenarios,
)

from .risk_sensitivities import (
    RISK_PROFILES,
    RiskProfile,
    FactorSensitivity,
    FactorDirection,
    Sensitivity,
    get_risk_affected_goals,
    get_risks_affecting_goal,
)

from .risk_calculator import (
    calculate_adjusted_probability,
    calculate_scenario_risk_profile,
    compare_scenarios_by_goal,
    get_scenario_risk_summary,
    print_scenario_comparison,
    ScenarioRiskResult,
    ScenarioRiskProfile,
)

from .goal_impacts import (
    GOALS,
    RISK_GOAL_IMPACTS,
    GoalDefinition,
    RiskGoalImpact,
    ImpactUnit,
    get_impacts_for_risk,
    get_impacts_for_goal,
    pert_mean,
)

from .goal_scoring import (
    calculate_scenario_goal_profile,
    calculate_weighted_score,
    rank_scenarios,
    compare_scenarios_by_goals,
    find_best_scenario_per_goal,
    GoalScore,
    GoalRiskContribution,
    ScenarioGoalProfile,
    WeightedScenarioScore,
    WEIGHTS_BALANCED,
    WEIGHTS_SPEED_FOCUSED,
    WEIGHTS_FISCAL_FOCUSED,
    WEIGHTS_SOCIAL_FOCUSED,
    WEIGHTS_CONTROL_FOCUSED,
    WEIGHTS_CITY_CRO,
)

__all__ = [
    # Structural factors
    "STRUCTURAL_FACTORS",
    "SCENARIO_FACTORS",
    "StructuralFactor",
    "ScenarioFactors",
    "get_scenario_profile",
    "compare_scenarios",
    # Risk profiles
    "RISK_PROFILES",
    "RiskProfile",
    "FactorSensitivity",
    "FactorDirection",
    "Sensitivity",
    "get_risk_affected_goals",
    "get_risks_affecting_goal",
    # Risk calculator
    "calculate_adjusted_probability",
    "calculate_scenario_risk_profile",
    "compare_scenarios_by_goal",
    "get_scenario_risk_summary",
    "print_scenario_comparison",
    "ScenarioRiskResult",
    "ScenarioRiskProfile",
    # Goal impacts
    "GOALS",
    "RISK_GOAL_IMPACTS",
    "GoalDefinition",
    "RiskGoalImpact",
    "ImpactUnit",
    "get_impacts_for_risk",
    "get_impacts_for_goal",
    "pert_mean",
    # Goal scoring
    "calculate_scenario_goal_profile",
    "calculate_weighted_score",
    "rank_scenarios",
    "compare_scenarios_by_goals",
    "find_best_scenario_per_goal",
    "GoalScore",
    "GoalRiskContribution",
    "ScenarioGoalProfile",
    "WeightedScenarioScore",
    "WEIGHTS_BALANCED",
    "WEIGHTS_SPEED_FOCUSED",
    "WEIGHTS_FISCAL_FOCUSED",
    "WEIGHTS_SOCIAL_FOCUSED",
    "WEIGHTS_CONTROL_FOCUSED",
    "WEIGHTS_CITY_CRO",
]
