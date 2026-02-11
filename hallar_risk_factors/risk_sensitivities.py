"""
Risk Sensitivity to Structural Factors

For each risk, we define:
1. Which factors affect it
2. Whether higher factor = lower risk (protective) or higher risk (exposure)
3. The sensitivity strength (how much the factor matters)

v4 — February 2026
  29 risks total:
  - Merged: R07→R10, R16→R12, R28→R27
  - Removed: R21
  - Fixed: R23 (F1 PROT→EXPO), R24/R26 (F6 removed), R04 (F7 added)
  - Added: R29, R30, R31, R32, R33
  - v5: Added R34, R35, R36, R37; expanded R30; removed R04→G9, R11→G9
  - All risks renamed to plain Icelandic
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class FactorDirection(Enum):
    """How a factor affects a risk."""
    PROTECTIVE = "protective"  # Higher factor score = LOWER risk
    EXPOSURE = "exposure"      # Higher factor score = HIGHER risk


class Sensitivity(Enum):
    """How sensitive the risk is to this factor."""
    LOW = 0.5
    MEDIUM = 1.0
    HIGH = 1.5
    CRITICAL = 2.0


@dataclass
class FactorSensitivity:
    """How a risk responds to a single factor."""
    factor_id: str
    direction: FactorDirection
    sensitivity: Sensitivity
    rationale: str


@dataclass
class RiskProfile:
    """Complete risk definition with base parameters and factor sensitivities."""
    risk_id: str
    name_is: str
    name_en: str
    category: str
    base_prob_low: float
    base_prob_likely: float
    base_prob_high: float
    affected_goals: List[str]
    sensitivities: List[FactorSensitivity] = field(default_factory=list)
    requires_factors: Optional[Dict[str, tuple]] = None


RISK_PROFILES: Dict[str, RiskProfile] = {
    # ═══════════════════════════════════════════════════════════
    # SKIPULAG OG LEYFI (6 risks)
    # ═══════════════════════════════════════════════════════════
    "R01": RiskProfile(
        risk_id="R01",
        name_is="Seinkun á deiliskipulagi",
        name_en="Zoning Plan Delays",
        category="Skipulag og leyfi",
        base_prob_low=0.20, base_prob_likely=0.40, base_prob_high=0.65,
        affected_goals=["G1", "G2", "G4"],
        sensitivities=[
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Fagleg stjórnun flýtir samskiptum við skipulagsyfirvöld"),
            FactorSensitivity("F6", FactorDirection.PROTECTIVE, Sensitivity.LOW,
                              "Borgin sem eigandi getur forgangsraðað ferli, en er samt háð formlegu ferli"),
        ],
    ),
    "R02": RiskProfile(
        risk_id="R02",
        name_is="Kæra á deiliskipulagi",
        name_en="Zoning Appeal",
        category="Skipulag og leyfi",
        base_prob_low=0.10, base_prob_likely=0.25, base_prob_high=0.45,
        affected_goals=["G1", "G2", "G4", "G5", "G9"],
        sensitivities=[
            FactorSensitivity("F6", FactorDirection.EXPOSURE, Sensitivity.LOW,
                              "Borgarverkefni fá meiri athygli og eru líklegri til kæru"),
        ],
    ),
    "R03": RiskProfile(
        risk_id="R03",
        name_is="Skipulag hentar ekki markaði",
        name_en="Market Mismatch",
        category="Skipulag og leyfi",
        base_prob_low=0.15, base_prob_likely=0.35, base_prob_high=0.60,
        affected_goals=["G2", "G3", "G5", "G10"],
        sensitivities=[
            # F4 reduced HIGH→LOW: Integration helps contractor flag buildability
            # issues, but market mismatch is about DEMAND (unit mix, price point).
            # That insight comes from the developer/fund, not the builder.
            FactorSensitivity("F4", FactorDirection.PROTECTIVE, Sensitivity.LOW,
                              "Samþætting gefur smá innsýn í byggjanleika en verktaki þekkir ekki markaðinn"),
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Fagleg stjórnun gerir markaðsrannsóknir og lagar áætlanir"),
        ],
    ),
    "R04": RiskProfile(
        risk_id="R04",
        name_is="Verktakar óska breytinga á skipulagi",
        name_en="Contractor Change Requests",
        category="Skipulag og leyfi",
        base_prob_low=0.30, base_prob_likely=0.55, base_prob_high=0.80,
        affected_goals=["G1", "G2", "G3", "G5", "G10"],
        sensitivities=[
            FactorSensitivity("F4", FactorDirection.PROTECTIVE, Sensitivity.CRITICAL,
                              "Ef sami aðili skipuleggur og byggir þarf hann ekki breytingar"),
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Fagleg stjórnun sér breytingabeiðnir fyrir og kemur í veg fyrir þær"),
            FactorSensitivity("F7", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Sterk samningsstaða borgar takmarkar heimild verktaka til breytinga"),
        ],
    ),
    "R05": RiskProfile(
        risk_id="R05",
        name_is="Tafir vegna umhverfismats",
        name_en="Environmental Assessment Delays",
        category="Skipulag og leyfi",
        base_prob_low=0.08, base_prob_likely=0.18, base_prob_high=0.35,
        affected_goals=["G1", "G2"],
        sensitivities=[
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.LOW,
                              "Fagleg stjórnun getur flýtt en ferlið er ytra"),
        ],
    ),
    "R06": RiskProfile(
        risk_id="R06",
        name_is="Fornleifafundir stöðva framkvæmdir",
        name_en="Archaeological Findings",
        category="Skipulag og leyfi",
        base_prob_low=0.03, base_prob_likely=0.10, base_prob_high=0.20,
        affected_goals=["G1", "G4"],
        sensitivities=[],
    ),
    # ═══════════════════════════════════════════════════════════
    # INNVIÐIR (3 risks — R07 merged into R10)
    # ═══════════════════════════════════════════════════════════
    "R08": RiskProfile(
        risk_id="R08",
        name_is="Kostnaður við innviði umfram áætlun",
        name_en="Infrastructure Cost Overrun",
        category="Innviðir",
        base_prob_low=0.20, base_prob_likely=0.45, base_prob_high=0.70,
        affected_goals=["G4", "G6"],
        sensitivities=[
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Fagleg stjórnun fylgist með kostnaði og umfangi"),
            FactorSensitivity("F7", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Sterkir samningar takmarka áhættu borgar eða deila henni"),
            # F4 REMOVED: Housing planning-construction integration has no
            # bearing on infrastructure costs. Infra (roads, utilities, schools)
            # is a separate workstream with its own procurement and design.
        ],
    ),
    "R09": RiskProfile(
        risk_id="R09",
        name_is="Gallar í innviðum koma í ljós",
        name_en="Infrastructure Quality Defects",
        category="Innviðir",
        base_prob_low=0.10, base_prob_likely=0.25, base_prob_high=0.45,
        affected_goals=["G4", "G6", "G7"],
        sensitivities=[
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Fagleg stjórnun framfylgir gæðakröfum"),
            FactorSensitivity("F7", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Sterkir samningar innihalda gæðakröfur og ábyrgðir"),
            FactorSensitivity("F6", FactorDirection.PROTECTIVE, Sensitivity.LOW,
                              "Borgin sem eigandi krefst hærri gæðastaðla (skólar, leikvellir, götur)"),
            # F2 REMOVED: Housing contractor strength is irrelevant to
            # infrastructure quality. Infra is built by specialized firms
            # under separate city/Veitur contracts.
        ],
    ),
    "R10": RiskProfile(
        risk_id="R10",
        name_is="Innviðaframkvæmdir og veitur seinkast",
        name_en="Infrastructure and Utilities Delays",
        category="Innviðir",
        # Merged with R07 (Veitur OR). Covers both general infra delays
        # and utility connection delays (known bottleneck in Reykjavik).
        base_prob_low=0.15, base_prob_likely=0.38, base_prob_high=0.60,
        affected_goals=["G1", "G2", "G6"],
        sensitivities=[
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Fagleg stjórnun samhæfir tímaáætlun og sér vandamál fyrir"),
            FactorSensitivity("F6", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Borgin sem eigandi getur þrýst á Veitur OR en opinber innkaup og nefndavinna seinka líka"),
            FactorSensitivity("F1", FactorDirection.EXPOSURE, Sensitivity.MEDIUM,
                              "Fleiri aðilar = meiri samhæfing = meiri töf"),
        ],
    ),
    # ═══════════════════════════════════════════════════════════
    # FRAMKVÆMDIR (6 risks — R16 merged into R12)
    # ═══════════════════════════════════════════════════════════
    "R11": RiskProfile(
        risk_id="R11",
        name_is="Verktaki verður gjaldþrota",
        name_en="Contractor Bankruptcy",
        category="Framkvæmdir",
        base_prob_low=0.05, base_prob_likely=0.15, base_prob_high=0.30,
        affected_goals=["G2", "G5", "G8", "G10"],
        sensitivities=[
            FactorSensitivity("F2", FactorDirection.PROTECTIVE, Sensitivity.CRITICAL,
                              "Sterkir verktakar verða ekki gjaldþrota. Veikir gera."),
            FactorSensitivity("F3", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Þolinmótt fjármagn getur stutt verktaka í erfiðleikum"),
            FactorSensitivity("F1", FactorDirection.EXPOSURE, Sensitivity.MEDIUM,
                              "Fleiri smáverktakar = meiri líkur á gjaldþroti hjá einhverjum"),
            FactorSensitivity("F7", FactorDirection.PROTECTIVE, Sensitivity.LOW,
                              "Step-in réttindi gera borgini kleift að skipta um verktaka"),
        ],
    ),
    "R12": RiskProfile(
        risk_id="R12",
        name_is="Byggingarkostnaður og efnisverð umfram áætlun",
        name_en="Construction and Material Cost Overrun",
        category="Framkvæmdir",
        # Merged with R16 (efnisverð hækkar). Covers both general
        # construction cost overruns and material price spikes.
        base_prob_low=0.20, base_prob_likely=0.45, base_prob_high=0.70,
        affected_goals=["G2", "G3", "G5", "G10"],
        sensitivities=[
            FactorSensitivity("F4", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Samþætting = verktaki þekkir verkið, færri óvæntar hækkanir"),
            # F2 reduced HIGH→MEDIUM: Integration (F4) is the primary cost reducer.
            # Contractor strength helps but is secondary — avoid double-counting.
            FactorSensitivity("F2", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Sterkir verktakar halda betur utan um kostnað en samþætting er aðaláhrifin"),
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Fagleg stjórnun fylgist með kostnaði og sér vandamál snemma"),
            FactorSensitivity("F3", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Þolinmótt fjármagn getur beðið eftir betri efnisverðum í stað skelfingarneyðarkaupa"),
        ],
    ),
    "R13": RiskProfile(
        risk_id="R13",
        name_is="Byggingaframkvæmdir dragast",
        name_en="Construction Delays",
        category="Framkvæmdir",
        base_prob_low=0.20, base_prob_likely=0.42, base_prob_high=0.68,
        affected_goals=["G2"],
        sensitivities=[
            # F2 reduced HIGH→MEDIUM: Integration (F4) is the primary delay
            # preventer. Contractor strength helps secondarily.
            FactorSensitivity("F2", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Sterkir verktakar standa betur við tímaáætlun en samþætting er aðaláhrifin"),
            FactorSensitivity("F4", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Samþætting = engin biðtími milli skipulags og framkvæmda"),
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Fagleg stjórnun þrýstir á tímaáætlun"),
            FactorSensitivity("F1", FactorDirection.EXPOSURE, Sensitivity.MEDIUM,
                              "Fleiri aðilar = fleiri viðmót = meiri hætta á töfum"),
        ],
    ),
    "R14": RiskProfile(
        risk_id="R14",
        name_is="Gæðavandamál í byggingum",
        name_en="Apartment Quality Defects",
        category="Framkvæmdir",
        base_prob_low=0.15, base_prob_likely=0.35, base_prob_high=0.58,
        affected_goals=["G8"],
        sensitivities=[
            FactorSensitivity("F2", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Sterkir verktakar hafa gæðakerfi og reynslu"),
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Fagleg stjórnun framfylgir gæðakröfum"),
            FactorSensitivity("F7", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Sterkir samningar innihalda gæðakröfur og viðurlög"),
        ],
    ),
    "R15": RiskProfile(
        risk_id="R15",
        name_is="Ekki nóg fagfólk til ráðningar",
        name_en="Labor Shortage",
        category="Framkvæmdir",
        base_prob_low=0.15, base_prob_likely=0.35, base_prob_high=0.58,
        affected_goals=["G2", "G8"],
        sensitivities=[
            FactorSensitivity("F2", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Sterkir verktakar laða að sér bestu fólkið og eiga birgðir af starfsfólki"),
            FactorSensitivity("F1", FactorDirection.EXPOSURE, Sensitivity.MEDIUM,
                              "Margir aðilar keppa um sama vinnuaflið á sama svæði"),
        ],
    ),
    "R17": RiskProfile(
        risk_id="R17",
        name_is="Léleg samhæfing milli verktaka",
        name_en="Coordination Failure Between Contractors",
        category="Framkvæmdir",
        base_prob_low=0.20, base_prob_likely=0.45, base_prob_high=0.72,
        affected_goals=["G1", "G2", "G7", "G8"],
        sensitivities=[
            FactorSensitivity("F1", FactorDirection.EXPOSURE, Sensitivity.CRITICAL,
                              "Fleiri aðilar = veldisvöxtur í samhæfingarþörf"),
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Fagleg stjórnun er samhæfing"),
            FactorSensitivity("F4", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Samþætting minnkar viðmót milli aðila"),
            FactorSensitivity("F2", FactorDirection.PROTECTIVE, Sensitivity.LOW,
                              "Sterkir verktakar hafa innra samhæfingarkerfi"),
        ],
    ),
    # ═══════════════════════════════════════════════════════════
    # MARKAÐUR (3 risks — R21 removed)
    # ═══════════════════════════════════════════════════════════
    "R18": RiskProfile(
        risk_id="R18",
        name_is="Eftirspurn eftir íbúðum minnkar",
        name_en="Demand Decline",
        category="Markaður",
        base_prob_low=0.08, base_prob_likely=0.22, base_prob_high=0.42,
        affected_goals=["G2", "G5"],
        sensitivities=[
            FactorSensitivity("F3", FactorDirection.PROTECTIVE, Sensitivity.CRITICAL,
                              "Þolinmótt fjármagn bíður eftir markaðnum. Bankar kalla lán."),
        ],
    ),
    "R19": RiskProfile(
        risk_id="R19",
        name_is="Íbúðaverð lækkar á markaði",
        name_en="Price Decline",
        category="Markaður",
        base_prob_low=0.10, base_prob_likely=0.25, base_prob_high=0.45,
        affected_goals=["G5"],
        sensitivities=[
            FactorSensitivity("F3", FactorDirection.PROTECTIVE, Sensitivity.CRITICAL,
                              "Lífeyrissjóðir geta haldið um eignir. Bankar geta ekki."),
        ],
    ),
    "R20": RiskProfile(
        risk_id="R20",
        name_is="Vextir hækka og fjármögnun dýrkar",
        name_en="Interest Rate Increases",
        category="Markaður",
        base_prob_low=0.12, base_prob_likely=0.28, base_prob_high=0.48,
        affected_goals=["G2", "G3", "G5"],
        sensitivities=[
            FactorSensitivity("F3", FactorDirection.PROTECTIVE, Sensitivity.CRITICAL,
                              "Lífeyrissjóðir = eigið fé, vextir skipta litlu. Bankar = stórt vandamál."),
        ],
    ),
    # ═══════════════════════════════════════════════════════════
    # FJÁRMÖGNUN (2 risks)
    # ═══════════════════════════════════════════════════════════
    "R22": RiskProfile(
        risk_id="R22",
        name_is="Fjármögnun bregst",
        name_en="Financing Unavailable",
        category="Fjármögnun",
        base_prob_low=0.05, base_prob_likely=0.15, base_prob_high=0.35,
        affected_goals=["G2", "G5"],
        sensitivities=[
            FactorSensitivity("F3", FactorDirection.PROTECTIVE, Sensitivity.CRITICAL,
                              "Lífeyrissjóðir hafa bundið fé. Bankafjármögnun getur þornað."),
            # F2 REMOVED: Financing availability depends on project economics,
            # market conditions, and capital source (F3). Contractor strength
            # has negligible effect on whether funding exists.
        ],
    ),
    "R23": RiskProfile(
        risk_id="R23",
        name_is="Lífeyrissjóður dregur sig út",
        name_en="Pension Fund Withdrawal",
        category="Fjármögnun",
        base_prob_low=0.03, base_prob_likely=0.10, base_prob_high=0.22,
        affected_goals=["G2", "G5", "G9"],
        sensitivities=[
            # v4 FIX: Changed from PROTECTIVE to EXPOSURE.
            # More owners = LESS dependent on one fund leaving.
            # Single fund = catastrophic if it leaves.
            FactorSensitivity("F1", FactorDirection.EXPOSURE, Sensitivity.HIGH,
                              "Einn eigandi = ef sjóðurinn hættir er allt búið. Fleiri = dreifð áhætta."),
        ],
        requires_factors={"F3": (3, 5)},
    ),
    # ═══════════════════════════════════════════════════════════
    # STJÓRNMÁL OG SAMFÉLAG (3 risks)
    # ═══════════════════════════════════════════════════════════
    "R24": RiskProfile(
        risk_id="R24",
        name_is="Nýr meirihluti breytir um stefnu",
        name_en="Political Change",
        category="Stjórnmál og samfélag",
        base_prob_low=0.10, base_prob_likely=0.25, base_prob_high=0.45,
        affected_goals=["G2", "G5", "G9", "G10"],
        sensitivities=[
            # v4 FIX: F6 EXPOSURE removed.
            # Political change is an external event. The new council still has
            # control — they just change priorities. City ownership doesn't
            # increase or decrease this risk.
        ],
    ),
    "R25": RiskProfile(
        risk_id="R25",
        name_is="Nýjar reglugerðir trufla verkefnið",
        name_en="Regulatory Changes",
        category="Stjórnmál og samfélag",
        base_prob_low=0.05, base_prob_likely=0.12, base_prob_high=0.25,
        affected_goals=["G1", "G2"],
        sensitivities=[],
    ),
    "R26": RiskProfile(
        risk_id="R26",
        name_is="Íbúar og hagsmunaaðilar mótmæla verkefninu",
        name_en="Public Opposition",
        category="Stjórnmál og samfélag",
        base_prob_low=0.08, base_prob_likely=0.20, base_prob_high=0.38,
        affected_goals=["G1", "G2", "G5", "G9"],
        sensitivities=[
            # v4 FIX: F6 EXPOSURE removed.
            # Public opposition affects all scenarios. City ownership means
            # the city can actually respond and adapt, not that it's more
            # vulnerable.
        ],
    ),
    # ═══════════════════════════════════════════════════════════
    # VERKEFNISSTJÓRNUN OG SAMNINGAR (1 risk — R28 merged into R27)
    # ═══════════════════════════════════════════════════════════
    "R27": RiskProfile(
        risk_id="R27",
        name_is="Eigendur og samningsaðilar ná ekki saman",
        name_en="Multi-Party Coordination and Contractual Failure",
        category="Verkefnisstjórnun og samningar",
        # Merged with R28 (samningságreiningur). Covers both informal
        # owner disagreements and formal contractual disputes.
        base_prob_low=0.12, base_prob_likely=0.30, base_prob_high=0.55,
        affected_goals=["G1", "G2", "G4", "G5", "G9"],
        sensitivities=[
            FactorSensitivity("F1", FactorDirection.EXPOSURE, Sensitivity.CRITICAL,
                              "Fleiri eigendur = fleiri samningar = fleiri deilur"),
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Fagleg stjórnun sér um samskipti og kemur í veg fyrir árekstra"),
            FactorSensitivity("F7", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Skýrir samningar draga úr túlkunarágreiningi"),
        ],
    ),
    # ═══════════════════════════════════════════════════════════
    # NEW RISKS (5 risks)
    # ═══════════════════════════════════════════════════════════
    "R29": RiskProfile(
        risk_id="R29",
        name_is="Ábyrgð á göllum eftir afhendingu",
        name_en="Latent Defect Liability",
        category="Framkvæmdir",
        base_prob_low=0.15, base_prob_likely=0.35, base_prob_high=0.55,
        affected_goals=["G4", "G7", "G8"],
        sensitivities=[
            FactorSensitivity("F7", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Sterkir samningar innihalda ábyrgðir og tryggingar"),
            FactorSensitivity("F2", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Sterkir verktakar standa við ábyrgðir og eru til staðar árum síðar"),
            # F6 EXPOSURE removed: City ownership affects who PAYS for defects
            # (impact layer), not whether defects EXIST (probability layer).
            # Defect probability depends on build quality (F2) and contractual
            # protections (F7), not ownership structure.
        ],
    ),
    "R30": RiskProfile(
        risk_id="R30",
        # v5: Expanded from "Bad Initial Deal" to include value capture failure.
        # Covers: (a) city negotiates poorly, (b) intermediary resells byggingarréttur
        # at markup, city loses the land value uplift.
        name_is="Borgin missir af virðisaukningu lands",
        name_en="City Value Capture Failure",
        category="Verkefnisstjórnun og samningar",
        base_prob_low=0.15, base_prob_likely=0.30, base_prob_high=0.50,
        affected_goals=["G3", "G4", "G9", "G10"],
        sensitivities=[
            FactorSensitivity("F7", FactorDirection.PROTECTIVE, Sensitivity.CRITICAL,
                              "Sterk samningsstaða borgar kemur í veg fyrir undirverðssölu og tryggir hlut borgar í virðisaukningu"),
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Fagleg stjórnun metur markaðsvirði réttinda og tryggir sanngjarnan samning"),
            # v5: F6 raised MEDIUM→HIGH. When city doesn't own (F6=1), it sells
            # byggingarréttur to intermediary who captures the markup. F6=5 means
            # the city IS the developer — no intermediary extraction possible.
            FactorSensitivity("F6", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Borgin sem eigandi þarf ekki að selja réttindi — engin millisala, engin virðisaukning tapaðist"),
        ],
    ),
    "R31": RiskProfile(
        risk_id="R31",
        name_is="Áfangar verkefnisins samræmast ekki",
        name_en="Phase Coordination Failure",
        category="Verkefnisstjórnun og samningar",
        base_prob_low=0.10, base_prob_likely=0.25, base_prob_high=0.45,
        affected_goals=["G1", "G2", "G4", "G5"],
        sensitivities=[
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Fagleg stjórnun skipuleggur áfanga og tryggir samhengisáætlun"),
            FactorSensitivity("F1", FactorDirection.EXPOSURE, Sensitivity.MEDIUM,
                              "Fleiri aðilar = erfiðara að samhæfa milli áfanga"),
            FactorSensitivity("F4", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Samþætting tryggir samhengi skipulags og framkvæmda milli áfanga"),
        ],
    ),
    "R32": RiskProfile(
        risk_id="R32",
        name_is="Borgin vantar fólk og þekkingu til eftirlits",
        name_en="City Institutional Capacity Risk",
        category="Stjórnmál og samfélag",
        base_prob_low=0.12, base_prob_likely=0.28, base_prob_high=0.48,
        affected_goals=["G5", "G7", "G9"],
        sensitivities=[
            FactorSensitivity("F6", FactorDirection.EXPOSURE, Sensitivity.MEDIUM,
                              "Meira eignarhald = meiri stjórnunarbyrði á borgina"),
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Faglegur ytri verkefnastjóri minnkar álagið á borgina"),
        ],
    ),
    "R33": RiskProfile(
        risk_id="R33",
        name_is="Félagsleg blöndun nást ekki í framkvæmd",
        name_en="Social Mix Enforcement Failure",
        category="Stjórnmál og samfélag",
        base_prob_low=0.15, base_prob_likely=0.35, base_prob_high=0.58,
        affected_goals=["G10"],
        sensitivities=[
            FactorSensitivity("F7", FactorDirection.PROTECTIVE, Sensitivity.CRITICAL,
                              "Sterkir samningar eru eina tækið til að framfylgja félagslegri blöndun"),
            FactorSensitivity("F6", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Borgin sem eigandi getur beint tryggt hagkvæmar íbúðir"),
        ],
    ),
    # ═══════════════════════════════════════════════════════════
    # v5 ADDITIONS (4 risks)
    # ═══════════════════════════════════════════════════════════
    "R34": RiskProfile(
        risk_id="R34",
        name_is="Skattaleg flækja vegna eignarhalds borgar",
        name_en="Tax Complications from City Ownership",
        category="Fjármögnun",
        # High base prob — user: "almost certain" in city partnership scenarios.
        # Tax structuring of municipal-private partnerships is inherently complex
        # (corporate income tax, VAT, transfer pricing, EEA state aid rules).
        base_prob_low=0.40, base_prob_likely=0.65, base_prob_high=0.85,
        affected_goals=["G2", "G4", "G9"],
        sensitivities=[
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Fagleg stjórnun fær skattaráðgjöf snemma og skipuleggur rétt"),
            FactorSensitivity("F7", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Sterkir samningar skilgreina skattaábyrgð og úthlutun"),
        ],
        # Only fires when city is commercial co-owner (F6=3-4).
        # F6=5 (S1) is municipal-led, tax-exempt activity.
        # F6=1 is private, no city tax issue.
        requires_factors={"F6": (3, 4)},
    ),
    "R35": RiskProfile(
        risk_id="R35",
        name_is="Útboðsreglur hægja á og takmarka val",
        name_en="Procurement Rules Constrain and Delay",
        category="Skipulag og leyfi",
        # EEA public procurement: mandatory tenders, minimum timelines,
        # standstill periods, appeal rights. The rules are certain; the risk
        # is that they cause meaningful delays and contractor quality issues.
        base_prob_low=0.35, base_prob_likely=0.55, base_prob_high=0.80,
        affected_goals=["G1", "G2", "G5"],
        sensitivities=[
            FactorSensitivity("F6", FactorDirection.EXPOSURE, Sensitivity.HIGH,
                              "Meira eignarhald borgar = strangari útboðsskylda og lengri ferlar"),
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Fagleg stjórnun vinnur útboðsferla hratt og rétt"),
        ],
        # Only fires when city has ownership role (F6 ≥ 3).
        # Private scenarios are not bound by public procurement law.
        requires_factors={"F6": (3, 5)},
    ),
    "R36": RiskProfile(
        risk_id="R36",
        name_is="Erfitt að slíta samstarfi eða losa sig úr eignarhaldi",
        name_en="Partnership Exit / Dissolution Difficulty",
        category="Verkefnisstjórnun og samningar",
        # Low base probability — most partnerships survive to completion.
        # But when they fail, the unwinding is expensive and slow.
        base_prob_low=0.08, base_prob_likely=0.20, base_prob_high=0.40,
        affected_goals=["G2", "G4", "G5", "G9"],
        sensitivities=[
            FactorSensitivity("F1", FactorDirection.EXPOSURE, Sensitivity.HIGH,
                              "Fleiri aðilar = flóknara að slíta, fleiri hagsmunir í húfi"),
            FactorSensitivity("F7", FactorDirection.PROTECTIVE, Sensitivity.HIGH,
                              "Sterkir samningar innihalda útgönguákvæði og uppkaupsréttar"),
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Fagleg stjórnun sér ágreining snemma og miðlar málum"),
        ],
    ),
    "R37": RiskProfile(
        risk_id="R37",
        name_is="Hagsmunaárekstrar vegna tvíþætts hlutverks borgar",
        name_en="City Dual Role Conflict of Interest",
        category="Stjórnmál og samfélag",
        # City is both regulator (zoning, permits) and developer/owner.
        # Competitors and neighbors challenge decisions on grounds that
        # city has financial interest in the outcome.
        # Distinct from R02 (general zoning appeal) — this is specifically
        # about challenges BECAUSE the city profits from its own decisions.
        base_prob_low=0.20, base_prob_likely=0.40, base_prob_high=0.65,
        affected_goals=["G1", "G2", "G5", "G9"],
        sensitivities=[
            FactorSensitivity("F6", FactorDirection.EXPOSURE, Sensitivity.HIGH,
                              "Meira eignarhald = stærri fjárhagslegir hagsmunir = stærri skotmark"),
            FactorSensitivity("F7", FactorDirection.PROTECTIVE, Sensitivity.MEDIUM,
                              "Gagnsæir samningar og ferlar draga úr grundvelli kæra"),
            FactorSensitivity("F5", FactorDirection.PROTECTIVE, Sensitivity.LOW,
                              "Fagleg stjórnun viðheldur hreinleika ferla"),
        ],
        # Only fires when city has ownership (F6 ≥ 3).
        # At F6=1, city is just regulator — no conflict of interest.
        requires_factors={"F6": (3, 5)},
    ),
}


def get_risk_affected_goals(risk_id: str) -> List[str]:
    """Get list of goals affected by a risk."""
    profile = RISK_PROFILES.get(risk_id)
    return profile.affected_goals if profile else []


def get_risks_affecting_goal(goal_id: str) -> List[str]:
    """Get list of risks that affect a specific goal."""
    return [rid for rid, profile in RISK_PROFILES.items() if goal_id in profile.affected_goals]