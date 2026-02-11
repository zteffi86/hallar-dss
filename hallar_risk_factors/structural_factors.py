"""
Structural Factors that Drive Risk Magnitude Across Scenarios

These factors capture WHY risks differ between scenarios, not just THAT they differ.
Each scenario is scored on these factors, and risks are sensitive to specific factors.

v6 — February 2026
  Model: 6 factors (F1-F6) x 11 scenarios (S1-S11)
  Groups:
    Group A (S1-S3): Borgarverkefni (city-led)
    Group B (S4-S8): Sjóðaverkefni (pension fund-led)
    Group C (S9-S11): Einkaframkvæmdir (bank-financed)
  Changes from v5.1:
    - Removed S5 (nýtt fasteignaþróunarfélag as co-owner): identical
      factor profile to S4. Partner quality is a risk, not a scenario.
      New risk: "Reynsluleysi eða veikleiki samstarfsaðila"
    - S4 F5 dropped from 4 to 3: hired developer has professional
      skills but fee-based incentives, weaker than co-owner.
    - Renumbered: old S6->S5, S7->S6, S8->S7, S9->S8, S10->S9,
      S11->S10, S12->S11
  Previous changes (v5/v5.1):
    - F7 (Samningsstyrkur) removed: contractual leverage is a policy
      choice available in all scenarios. Moved to mitigation layer.
    - Scenarios grouped by ownership type and renamed.
  Full ID mapping (original -> current):
    S1->S1, S10->S2, S11->S3, S2->S4, S5->S5, S4->S6,
    S12->S7, S6->S8, S8->S9, S7->S10, S9->S11
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
        description_is="Fjárhagslegur og rekstrarlegur styrkur þess aðila sem byggir. Nær yfir stærð, fjárhagsstöðu, tæknilega getu og reynslu af stórum verkefnum.",
        description_en="Financial and operational strength of the party that builds. Covers scale, financial position, technical capability and large-project experience.",
        scale_low="1 = Veikir/margir smáir verktakar",
        scale_high="5 = Sterkur aðalverktaki með reynslu og fjárhagslegan bakhjarl",
    ),
    "F3": StructuralFactor(
        id="F3",
        name_is="Fjármögnunarþol",
        name_en="Capital Resilience",
        description_is="Hversu vel þolir fjármögnunin sveiflur og tafir? Lífeyrissjóðir hafa 30–50 ára sjóndeildarhring og þola niðursveiflu. Bankalán krefjast afborgana frá fyrsta degi og þola ekki tekjufall.",
        description_en="How well can the financing absorb volatility and delays? Pension funds have 30-50 year horizons. Bank loans demand repayment from day one.",
        scale_low="1 = Bankalán eingöngu (óþolinmótt, þolir ekki tafir)",
        scale_high="5 = Lífeyrissjóðir eingöngu (þolinmótt, þolir niðursveiflu)",
    ),
    "F4": StructuralFactor(
        id="F4",
        name_is="Samræming skipulags og framkvæmda",
        name_en="Planning-Execution Integration",
        description_is="Kemur byggingarþekking inn í skipulagsferlið frá upphafi? Þegar sá sem byggir hefur áhrif á deiliskipulagshönnun minnka breytingabeiðnir, samhæfingarvandamál og tafir. Þegar skipulag og framkvæmd eru aðskilin þarf að 'þýða' milli hönnunar og byggingar.",
        description_en="Does construction knowledge inform the design process from the start? When the builder influences the zoning design, change requests and coordination problems decrease. When planning and execution are separated, translation gaps emerge.",
        scale_low="1 = Algjörlega aðskilið (hönnun án byggingarinnsýnar)",
        scale_high="5 = Sami aðili skipuleggur og byggir (engin þýðingarbil)",
    ),
    "F5": StructuralFactor(
        id="F5",
        name_is="Fagleg stjórnun",
        name_en="Professional Management",
        description_is="Hversu sterk er fagleg verkefnisstjórnun og hvatar hennar? Mælir bæði gæði stjórnunar (reynsla, kerfi, mannauður) og hvatasamræmingu (er stjórnandi meðeigandi eða ráðinn?). Nær einnig yfir heildarsýn yfir hverfisþróun — hvort einhver aðili skipuleggur hverfið sem heild (skóla, garða, götur, íbúðir saman) eða hvort hvert lóðarsvæði er hannað í einangrun. Fasteignaþróunarfélag sem meðeigandi með stofnanastyrkleika er efst á kvarðanum.",
        description_en="How strong is professional project management and its incentive alignment? Measures both management quality (experience, systems, staff) and incentives (is the manager a co-owner or hired?). Also captures neighborhood-level design coherence — whether someone plans the neighborhood as a whole (school, parks, streets, apartments together) or each plot is designed in isolation. An established real estate developer as co-owner is top of scale.",
        scale_low="1 = Engin samhæfð stjórnun (nefnd eða smáir verktakar á eigin vegum, engin heildarsýn)",
        scale_high="5 = Fasteignaþróunarfélag sem meðeigandi (stofnanaþekking + eiginhagsmunir + heildarsýn yfir hverfið)",
    ),
    "F6": StructuralFactor(
        id="F6",
        name_is="Reykjavíkurborg sem eigandi",
        name_en="City as Owner",
        description_is="Er borgin eigandi og framkvæmdaraðili, eða aðeins eftirlitsaðili sem samþykkir? ATH: Borgin hefur ALLTAF skipulagsvald (deiliskipulag, blöndunarkröfur, blágrænar lausnir) óháð þessum þætti. F6 mælir eignarhald UMFRAM þann grunn. Þetta er EINI tvístefnuþátturinn: eigandi-borg getur þrýst á Veitur og varðveitt virðisaukningu (verndandi), en lýtur útboðsreglum og verður pólitískt skotmark (afhjúpandi).",
        description_en="Is the city an owner and executor, or only a regulator that approves? NOTE: The city ALWAYS retains zoning authority (deiliskipulag, mix requirements, blue-green solutions) regardless of this factor. F6 measures ownership BEYOND that baseline. This is the ONLY dual-direction factor: city-as-owner can pressure Veitur and capture value uplift (protective), but is subject to procurement rules and political risk (exposure).",
        scale_low="1 = Borgin er aðeins eftirlitsaðili (samþykkir skipulag annarra)",
        scale_high="5 = Borgin er aðaleigandi og framkvæmdaraðili (stýrir hönnun og útboðum)",
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
        F1=2, F2=2, F3=3, F4=3, F5=2, F6=5,
    ),
    "S2": ScenarioFactors(
        scenario_id="S2",
        name_is="Reykjavíkurborg og lífeyrissjóðir eru eigendur",
        name_en="City + Pension Funds as Co-Owners",
        # Originally S10. Zoning pathway A (city involved in design)
        # F1=3: city political process + fund investment process = genuine complexity
        F1=3, F2=3, F3=4, F4=3, F5=3, F6=4,
    ),
    "S3": ScenarioFactors(
        scenario_id="S3",
        name_is="Reykjavíkurborg, lífeyrissjóðir og aðalverktaki eigendur",
        name_en="City + Pension Funds + Head Contractor as Co-Owners",
        # Originally S11. Zoning pathway A+C hybrid
        # F1=4: three co-owners with fundamentally different decision cultures
        F1=4, F2=5, F3=4, F4=5, F5=4, F6=3,
    ),

    # ═══════════════════════════════════════════════════════════
    # GROUP B: SJÓÐAVERKEFNI (Pension fund-led)
    # ═══════════════════════════════════════════════════════════
    "S4": ScenarioFactors(
        scenario_id="S4",
        name_is="Lífeyrissjóður er eigandi og ráðir fasteignaþróunarfélag",
        name_en="Pension Fund Hires Real Estate Developer (Fund Owns)",
        # Originally S2. Zoning pathway B: developer designs, fund owns
        # F5=3: professional skills but fee-based incentives (hired, not co-owner)
        F1=2, F2=3, F3=5, F4=3, F5=3, F6=1,
    ),
    "S5": ScenarioFactors(
        scenario_id="S5",
        name_is="Lífeyrissjóðir og stórt fasteignaþróunarfélag eru meðeigendur",
        name_en="Pension Funds + Established Real Estate Developer as Co-Owners",
        # Originally S5. Zoning pathway B: established developer designs
        # F2=4: strong contractor network through established developer
        # F5=5: institutional depth + ownership incentives + heildarsýn
        F1=2, F2=4, F3=5, F4=4, F5=5, F6=1,
    ),
    "S6": ScenarioFactors(
        scenario_id="S6",
        name_is="Lífeyrissjóður og aðalverktaki sameiginlegir eigendur",
        name_en="Pension Fund + Head Contractor as Co-Owners",
        # Originally S4. Zoning pathway C: builder designs
        F1=2, F2=5, F3=5, F4=5, F5=4, F6=1,
    ),
    "S7": ScenarioFactors(
        scenario_id="S7",
        name_is="Lífeyrissjóðir eru eigendur og ráða til sín aðalverktaka",
        name_en="Pension Fund Hires Head Contractor (Fund Owns)",
        # Originally S12. Zoning pathway B/C hybrid: contractor provides
        # buildability input but doesn't own the design process
        # F2=4: head contractor is strong by definition
        # F4=4: buildability input during planning, not full integration
        F1=2, F2=4, F3=5, F4=4, F5=4, F6=1,
    ),
    "S8": ScenarioFactors(
        scenario_id="S8",
        name_is="Innviðafélag lífeyrissjóða byggir innviði og selur BR",
        name_en="Pension Fund Builds Infrastructure, Sells Building Rights",
        # Originally S6. Two-phase: fund builds infrastructure, then sells BR
        # Building phase is essentially uncontrolled by the fund
        # F3=3: construction buyers use bank financing, not fund patience
        # F5=2: construction phase has no coordinated management
        F1=3, F2=2, F3=3, F4=1, F5=2, F6=1,
    ),

    # ═══════════════════════════════════════════════════════════
    # GROUP C: EINKAFRAMKVÆMDIR (Bank-financed / contractor-led)
    # ═══════════════════════════════════════════════════════════
    "S9": ScenarioFactors(
        scenario_id="S9",
        name_is="1 stór verktaki er eigandi með bankafjármögnun",
        name_en="Bank Financing + Single Large Contractor",
        # Originally S8. Zoning pathway C: builder designs
        F1=1, F2=4, F3=1, F4=5, F5=4, F6=1,
    ),
    "S10": ScenarioFactors(
        scenario_id="S10",
        name_is="2–3 meðalstórir verktakar eigendur með bankafjármögnun",
        name_en="Bank Financing + 2-3 Mid-Size Contractors as Co-Owners",
        # Originally S7. Zoning pathway C: builders design
        F1=3, F2=4, F3=1, F4=4, F5=3, F6=1,
    ),
    "S11": ScenarioFactors(
        scenario_id="S11",
        name_is="Eigendur eru margir smáir verktakar",
        name_en="Many Small Contractors as Owners",
        # Originally S9. Worst-case baseline, no coordination
        # F3=1: small contractors are almost entirely bank-dependent
        F1=5, F2=1, F3=1, F4=1, F5=1, F6=1,
    ),
}


def get_scenario_profile(scenario_id: str) -> Dict[str, int]:
    """Get all factor scores for a scenario as a dict."""
    sf = SCENARIO_FACTORS.get(scenario_id)
    if not sf:
        return {}
    return {
        "F1": sf.F1, "F2": sf.F2, "F3": sf.F3, "F4": sf.F4,
        "F5": sf.F5, "F6": sf.F6,
    }


def compare_scenarios(s1: str, s2: str) -> Dict[str, tuple]:
    """Compare two scenarios factor by factor."""
    p1 = get_scenario_profile(s1)
    p2 = get_scenario_profile(s2)
    return {fid: (p1.get(fid, 0), p2.get(fid, 0)) for fid in STRUCTURAL_FACTORS.keys()}
