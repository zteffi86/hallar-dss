"""
Structural Factors that Drive Risk Magnitude Across Scenarios

These factors capture WHY risks differ between scenarios, not just THAT they differ.
Each scenario is scored on these factors, and risks are sensitive to specific factors.

v4 — February 2026
  - F1 renamed: Eigendafjöldi → Flækjustig ákvarðanatöku
  - S1: F4 raised 2→3, F7 raised 4→5
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class StructuralFactor:
    """Definition of a structural factor that drives risk."""
    id: str
    name_is: str
    name_en: str
    description_is: str
    description_en: str
    scale_low: str
    scale_high: str


STRUCTURAL_FACTORS: Dict[str, StructuralFactor] = {
    "F1": StructuralFactor(
        id="F1",
        name_is="Flækjustig ákvarðanatöku",
        name_en="Decision Complexity",
        description_is="Hversu flókið er að taka ákvarðanir? Hversu margir aðilar þurfa að samþykkja?",
        description_en="How complex is the decision-making? How many parties need to agree?",
        scale_low="1 = Einn aðili ákveður (einfalt)",
        scale_high="5 = Margir aðilar þurfa að samþykkja (flókið)",
    ),
    "F2": StructuralFactor(
        id="F2",
        name_is="Styrkur verktaka",
        name_en="Contractor Strength",
        description_is="Fjárhagslegur og rekstrarlegur styrkur verktaka.",
        description_en="Financial and operational strength of contractor(s).",
        scale_low="1 = Veikir/margir smáir",
        scale_high="5 = Sterkur/samþættur",
    ),
    "F3": StructuralFactor(
        id="F3",
        name_is="Þolinmæði fjármagns",
        name_en="Capital Patience",
        description_is="Hversu þolinmótt er fjármagnið? Þolir niðursveiflu?",
        description_en="How patient is the capital? Can it weather downturns?",
        scale_low="1 = Bankalán eingöngu (óþolinmótt)",
        scale_high="5 = Lífeyrissjóðir eingöngu (þolinmótt)",
    ),
    "F4": StructuralFactor(
        id="F4",
        name_is="Samræming skipulags og framkvæmda",
        name_en="Planning-Execution Integration",
        description_is="Er sami aðili að skipuleggja og byggja?",
        description_en="Does the same party plan and build?",
        scale_low="1 = Algjörlega aðskilið",
        scale_high="5 = Fullkomlega samþætt",
    ),
    "F5": StructuralFactor(
        id="F5",
        name_is="Fagleg stjórnun",
        name_en="Professional Management",
        description_is="Er sérstakur faglegur verkefnastjóri með hvata?",
        description_en="Is there dedicated professional management with incentives?",
        scale_low="1 = Engin/nefndarstjórnun",
        scale_high="5 = Faglegur stjóri með eignarhlut",
    ),
    "F6": StructuralFactor(
        id="F6",
        name_is="Reykjavíkurorg sem eigandi",
        name_en="City as Owner",
        description_is="Er borgin eigandi að verkefninu?",
        description_en="Is the city an owner of the project?",
        scale_low="1 = Borgin er aðeins eftirlitsaðili",
        scale_high="5 = Borgin er aðaleigandi",
    ),
    "F7": StructuralFactor(
        id="F7",
        name_is="Samningsstyrkur Reykjavíkurborgar",
        name_en="City Contractual Leverage",
        description_is="Hversu sterk samningsstaða hefur borgin til að framfylgja markmiðum?",
        description_en="How strong is the city's contractual position to enforce goals?",
        scale_low="1 = Lítil áhrif eftir sölu",
        scale_high="5 = Sterk réttindi og step-in",
    ),
}


@dataclass
class ScenarioFactors:
    """Factor scores for a single scenario."""
    scenario_id: str
    name_is: str
    name_en: str
    F1: int  # Flækjustig ákvarðanatöku (1-5, higher = more complex)
    F2: int  # Verktakastyrkur (1-5, higher = stronger)
    F3: int  # Fjármögnunarþol (1-5, higher = more patient)
    F4: int  # Samræming (1-5, higher = more integrated)
    F5: int  # Fagleg stjórnun (1-5, higher = better)
    F6: int  # Borg eigandi (1-5, higher = more city ownership)
    F7: int  # Samningsstyrkur (1-5, higher = stronger city position)

    def get_factor(self, factor_id: str) -> int:
        return getattr(self, factor_id)


SCENARIO_FACTORS: Dict[str, ScenarioFactors] = {
    "S1": ScenarioFactors(
        scenario_id="S1",
        name_is="Borgin byggir innviði og selur byggingarrétt",
        name_en="Traditional City-Led",
        # F4: 2→3 — city both plans and oversees execution through procurement
        # F7: 4→5 — city runs everything, maximum enforcement power
        F1=2, F2=2, F3=3, F4=3, F5=2, F6=5, F7=5,
    ),
    "S2": ScenarioFactors(
        scenario_id="S2",
        name_is="Lífeyrissjóður eru eigendur sem ráða til sín verkefnastjóra",
        name_en="Pension Fund + Project Manager (Fund Owns)",
        F1=2, F2=3, F3=5, F4=3, F5=4, F6=1, F7=3,
    ),
    "S3": ScenarioFactors(
        scenario_id="S3",
        name_is="Lífeyrissjóður og verkefnastjóri eru meðeigendur",
        name_en="Pension Fund + Manager as Co-Owner",
        # F5: 4→5 — verkefnastjóri as co-owner matches scale definition exactly:
        # "Faglegur stjóri með eignarhlut". Co-ownership aligns incentives
        # and creates maximum personal accountability.
        F1=2, F2=3, F3=5, F4=3, F5=5, F6=1, F7=3,
    ),
    "S4": ScenarioFactors(
        scenario_id="S4",
        name_is="Lífeyrissjóður og aðalverktaki sameiginlegir eigendur",
        name_en="Pension Fund + Head Contractor as Co-Owner",
        F1=2, F2=5, F3=5, F4=5, F5=4, F6=1, F7=3,
    ),
    "S5": ScenarioFactors(
        scenario_id="S5",
        name_is="Lífeyrissjóðir eigendur með fasteignaþróunarfélagi",
        name_en="Pension Funds via Summa/Reitir + Subcontractors",
        # F1: 3→2 — funds delegate to developer, don't co-manage day-to-day
        # F5: 4→5 — fasteignaþróunarfélag as owner combines institutional
        # depth (systems, staff, multi-project experience) with ownership
        # incentives. This is the strongest professional management form.
        F1=2, F2=4, F3=5, F4=4, F5=5, F6=1, F7=3,
    ),
    "S6": ScenarioFactors(
        scenario_id="S6",
        name_is="Innviðafélag lífeyrissjóða byggir innviði og selur BR",
        name_en="Pension Fund Builds Infrastructure, Sells Rights",
        # F3: 4→3 — construction buyers use bank financing, not fund patience
        # F5: 3→2 — construction phase has no coordinated management
        F1=3, F2=2, F3=3, F4=1, F5=2, F6=1, F7=2,
    ),
    "S7": ScenarioFactors(
        scenario_id="S7",
        name_is="2–3 stórir verktakar eigendur með bankafjármögnun",
        name_en="Bank Financing + 2-3 Contractors as Co-Owners",
        F1=3, F2=4, F3=1, F4=4, F5=3, F6=1, F7=2,
    ),
    "S8": ScenarioFactors(
        scenario_id="S8",
        name_is="1 stór verktaki er eigandi með bankafjármögnun",
        name_en="Bank Financing + Single Large Contractor",
        F1=1, F2=4, F3=1, F4=5, F5=4, F6=1, F7=2,
    ),
    "S9": ScenarioFactors(
        scenario_id="S9",
        name_is="Margir smáir verktakar — engin samhæfing",
        name_en="Many Small Contractors",
        # F3: 2→1 — small contractors are almost entirely bank-dependent
        F1=5, F2=1, F3=1, F4=1, F5=1, F6=1, F7=1,
    ),
    "S10": ScenarioFactors(
        scenario_id="S10",
        name_is="Reykjavíkurborg og lífeyrissjóðir eru eigendur",
        name_en="City + Pension Funds as Co-Owners",
        # F1: 2→3 — city political process + fund investment process = genuine complexity
        F1=3, F2=3, F3=4, F4=3, F5=3, F6=4, F7=4,
    ),
    "S11": ScenarioFactors(
        scenario_id="S11",
        name_is="Reykjavíkurborg, lífeyrissjóðir og aðalverktaki eigendur",
        name_en="City + PF + Head Contractor as Co-Owners",
        # F1: 3→4 — three co-owners (city/fund/contractor) with fundamentally
        # different decision cultures, timelines, and incentives
        F1=4, F2=5, F3=4, F4=5, F5=4, F6=3, F7=4,
    ),
    "S12": ScenarioFactors(
        scenario_id="S12",
        name_is="Lífeyrissjóðir eru eigendur og ráða til sín aðalverktaka",
        name_en="Pension Fund + Head Contractor (Not Owner)",
        # F2: 3→4 — head contractor is strong by definition, ownership doesn't change capability
        # F4: 3→4 — even without ownership, aðalverktaki provides buildability
        # input during planning due to technical expertise. Stronger integration
        # than a generic project manager (S2) though not full integration (S4=5).
        F1=2, F2=4, F3=5, F4=4, F5=4, F6=1, F7=3,
    ),
}


def get_scenario_profile(scenario_id: str) -> Dict[str, int]:
    """Get all factor scores for a scenario as a dict."""
    sf = SCENARIO_FACTORS.get(scenario_id)
    if not sf:
        return {}
    return {
        "F1": sf.F1, "F2": sf.F2, "F3": sf.F3, "F4": sf.F4,
        "F5": sf.F5, "F6": sf.F6, "F7": sf.F7,
    }


def compare_scenarios(s1: str, s2: str) -> Dict[str, tuple]:
    """Compare two scenarios factor by factor."""
    p1 = get_scenario_profile(s1)
    p2 = get_scenario_profile(s2)
    return {fid: (p1.get(fid, 0), p2.get(fid, 0)) for fid in STRUCTURAL_FACTORS.keys()}
