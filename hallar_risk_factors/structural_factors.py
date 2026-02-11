"""
Structural Factors that Drive Risk Magnitude Across Scenarios

These factors capture WHY risks differ between scenarios, not just THAT they differ.
Each scenario is scored on these factors, and risks are sensitive to specific factors.

v5 — February 2026
  Scenario renumbering: grouped by ownership type
    Group A (S1–S3): Borgarverkefni (city-led)
    Group B (S4–S9): Sjóðaverkefni (pension fund-led)
    Group C (S10–S12): Einkaframkvæmdir (bank-financed)
  Scenario renames:
    S4 (was S2): verkefnastjóri → fasteignaþróunarfélag
    S5 (was S3): verkefnastjóri → nýtt fasteignaþróunarfélag
    S6 (was S5): clarified stórt fasteignaþróunarfélag
    S11 (was S7): stórir → meðalstórir verktakar
    S12 (was S9): renamed Eigendur eru margir smáir verktakar
  ID mapping (old → new):
    S1→S1, S10→S2, S11→S3, S2→S4, S3→S5, S5→S6,
    S4→S7, S12→S8, S6→S9, S8→S10, S7→S11, S9→S12
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
        name_is="Reykjavíkurborg sem eigandi",
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
    # ═══════════════════════════════════════════════════════════
    # GROUP A: BORGARVERKEFNI (City-led)
    # ═══════════════════════════════════════════════════════════
    "S1": ScenarioFactors(
        scenario_id="S1",
        name_is="Borgin byggir innviði og selur byggingarrétt",
        name_en="Traditional City-Led",
        # Zoning pathway A: city manages design via hugmyndasamkeppni/útboð
        F1=2, F2=2, F3=3, F4=3, F5=2, F6=5, F7=5,
    ),
    "S2": ScenarioFactors(
        scenario_id="S2",
        name_is="Reykjavíkurborg og lífeyrissjóðir eru eigendur",
        name_en="City + Pension Funds as Co-Owners",
        # Was S10. Zoning pathway A (city involved in design)
        # F1=3: city political process + fund investment process = genuine complexity
        F1=3, F2=3, F3=4, F4=3, F5=3, F6=4, F7=4,
    ),
    "S3": ScenarioFactors(
        scenario_id="S3",
        name_is="Reykjavíkurborg, lífeyrissjóðir og aðalverktaki eigendur",
        name_en="City + Pension Funds + Head Contractor as Co-Owners",
        # Was S11. Zoning pathway A+C hybrid (city and contractor both have design input)
        # F1=4: three co-owners with fundamentally different decision cultures
        F1=4, F2=5, F3=4, F4=5, F5=4, F6=3, F7=4,
    ),

    # ═══════════════════════════════════════════════════════════
    # GROUP B: SJÓÐAVERKEFNI (Pension fund-led)
    # ═══════════════════════════════════════════════════════════
    "S4": ScenarioFactors(
        scenario_id="S4",
        name_is="Lífeyrissjóður er eigandi og ráðir fasteignaþróunarfélag",
        name_en="Pension Fund Hires Real Estate Developer (Fund Owns)",
        # Was S2. Zoning pathway B: developer designs, fund owns
        # Renamed: verkefnastjóri → fasteignaþróunarfélag
        F1=2, F2=3, F3=5, F4=3, F5=4, F6=1, F7=3,
    ),
    "S5": ScenarioFactors(
        scenario_id="S5",
        name_is="Lífeyrissjóður og nýtt fasteignaþróunarfélag eru meðeigendur",
        name_en="Pension Fund + New Real Estate Developer as Co-Owners",
        # Was S3. Zoning pathway B: developer designs, co-ownership
        # Renamed: verkefnastjóri → nýtt fasteignaþróunarfélag
        # F5=5: co-ownership aligns incentives, even for newer developer
        F1=2, F2=3, F3=5, F4=3, F5=5, F6=1, F7=3,
    ),
    "S6": ScenarioFactors(
        scenario_id="S6",
        name_is="Lífeyrissjóðir og stórt fasteignaþróunarfélag eru meðeigendur",
        name_en="Pension Funds + Established Real Estate Developer as Co-Owners",
        # Was S5. Zoning pathway B: established developer designs
        # F2=4: strong contractor network through established developer
        # F5=5: institutional depth + ownership incentives
        F1=2, F2=4, F3=5, F4=4, F5=5, F6=1, F7=3,
    ),
    "S7": ScenarioFactors(
        scenario_id="S7",
        name_is="Lífeyrissjóður og aðalverktaki sameiginlegir eigendur",
        name_en="Pension Fund + Head Contractor as Co-Owners",
        # Was S4. Zoning pathway C: builder designs
        F1=2, F2=5, F3=5, F4=5, F5=4, F6=1, F7=3,
    ),
    "S8": ScenarioFactors(
        scenario_id="S8",
        name_is="Lífeyrissjóðir eru eigendur og ráða til sín aðalverktaka",
        name_en="Pension Fund Hires Head Contractor (Fund Owns)",
        # Was S12. Zoning pathway B/C hybrid: contractor provides
        # buildability input but doesn't own the design process
        # F2=4: head contractor is strong by definition
        # F4=4: buildability input during planning, not full integration
        F1=2, F2=4, F3=5, F4=4, F5=4, F6=1, F7=3,
    ),
    "S9": ScenarioFactors(
        scenario_id="S9",
        name_is="Innviðafélag lífeyrissjóða byggir innviði og selur BR",
        name_en="Pension Fund Builds Infrastructure, Sells Building Rights",
        # Was S6. Two-phase: fund builds infrastructure, then sells BR
        # Building phase is essentially uncontrolled by the fund
        # F3=3: construction buyers use bank financing, not fund patience
        # F5=2: construction phase has no coordinated management
        F1=3, F2=2, F3=3, F4=1, F5=2, F6=1, F7=2,
    ),

    # ═══════════════════════════════════════════════════════════
    # GROUP C: EINKAFRAMKVÆMDIR (Bank-financed / contractor-led)
    # ═══════════════════════════════════════════════════════════
    "S10": ScenarioFactors(
        scenario_id="S10",
        name_is="1 stór verktaki er eigandi með bankafjármögnun",
        name_en="Bank Financing + Single Large Contractor",
        # Was S8. Zoning pathway C: builder designs
        F1=1, F2=4, F3=1, F4=5, F5=4, F6=1, F7=2,
    ),
    "S11": ScenarioFactors(
        scenario_id="S11",
        name_is="2–3 meðalstórir verktakar eigendur með bankafjármögnun",
        name_en="Bank Financing + 2-3 Mid-Size Contractors as Co-Owners",
        # Was S7. Zoning pathway C: builders design
        # Renamed: stórir → meðalstórir
        F1=3, F2=4, F3=1, F4=4, F5=3, F6=1, F7=2,
    ),
    "S12": ScenarioFactors(
        scenario_id="S12",
        name_is="Eigendur eru margir smáir verktakar",
        name_en="Many Small Contractors as Owners",
        # Was S9. Worst-case baseline, no coordination
        # F3=1: small contractors are almost entirely bank-dependent
        F1=5, F2=1, F3=1, F4=1, F5=1, F6=1, F7=1,
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
