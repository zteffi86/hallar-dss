"""
Goal Impact Definitions

For each risk × goal combination, define:
- Impact unit (months, M ISK, percentage points, score points)
- Impact magnitude (best / likely / worst case)

This allows us to calculate:
  Expected Goal Impact = P(risk) × Impact_if_occurs

v4 — February 2026
  - R07 impacts merged into R10 (combined infra + utilities delays)
  - R16 impacts merged into R12 (combined construction + material costs)
  - R28 impacts merged into R27 (combined owner disputes + contractual)
  - R21 removed
  - R29–R33 added
  - v5: R30 expanded (added G4); R34–R37 added; R04→G9 removed; R11→G9 removed
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum


class ImpactUnit(Enum):
    """Units for goal impacts."""
    MONTHS = "months"
    MISK = "misk"
    PCT_POINTS = "pct_points"
    SCORE_POINTS = "score"


@dataclass
class GoalDefinition:
    """Definition of a city goal."""
    goal_id: str
    name_is: str
    name_en: str
    unit: ImpactUnit
    baseline: float
    direction: str  # "lower_better" or "higher_better"
    description: str


GOALS: Dict[str, GoalDefinition] = {
    "G1": GoalDefinition(
        goal_id="G1",
        name_is="Innviðahraði",
        name_en="Infrastructure Speed",
        unit=ImpactUnit.MONTHS,
        baseline=36.0,
        direction="lower_better",
        description="Months until infrastructure is ready for residents",
    ),
    "G2": GoalDefinition(
        goal_id="G2",
        name_is="Byggingarhraði",
        name_en="Construction Speed",
        unit=ImpactUnit.MONTHS,
        baseline=60.0,
        direction="lower_better",
        description="Months until housing is delivered",
    ),
    "G3": GoalDefinition(
        goal_id="G3",
        name_is="Hagkvæmni",
        name_en="Affordability",
        unit=ImpactUnit.PCT_POINTS,
        baseline=0.0,
        direction="lower_better",
        description="Percentage increase in price per m² above target",
    ),
    "G4": GoalDefinition(
        goal_id="G4",
        name_is="Fjárhagsleg niðurstaða",
        name_en="City Financial Outcome",
        unit=ImpactUnit.MISK,
        baseline=0.0,
        direction="lower_better",
        description="City cost overrun in M ISK",
    ),
    "G5": GoalDefinition(
        goal_id="G5",
        name_is="Líkur á fullnaði",
        name_en="Completion Probability",
        unit=ImpactUnit.PCT_POINTS,
        baseline=100.0,
        direction="higher_better",
        description="Probability project completes as planned",
    ),
    "G6": GoalDefinition(
        goal_id="G6",
        name_is="Kostnaðarstýring innviða",
        name_en="Infrastructure Budget Adherence",
        unit=ImpactUnit.PCT_POINTS,
        baseline=100.0,
        direction="higher_better",
        description="Probability of staying within infrastructure budget",
    ),
    "G7": GoalDefinition(
        goal_id="G7",
        name_is="Gæði innviða",
        name_en="Infrastructure Quality",
        unit=ImpactUnit.SCORE_POINTS,
        baseline=100.0,
        direction="higher_better",
        description="Infrastructure quality score (0-100)",
    ),
    "G8": GoalDefinition(
        goal_id="G8",
        name_is="Gæði bygginga",
        name_en="Construction Quality",
        unit=ImpactUnit.SCORE_POINTS,
        baseline=100.0,
        direction="higher_better",
        description="Construction quality score (0-100)",
    ),
    "G9": GoalDefinition(
        goal_id="G9",
        name_is="Stjórn borgar",
        name_en="City Control",
        unit=ImpactUnit.SCORE_POINTS,
        baseline=100.0,
        direction="higher_better",
        description="City's ability to enforce goals (0-100)",
    ),
    "G10": GoalDefinition(
        goal_id="G10",
        name_is="Félagsleg blöndun",
        name_en="Social Mix",
        unit=ImpactUnit.PCT_POINTS,
        baseline=30.0,
        direction="higher_better",
        description="Percentage of affordable housing achieved",
    ),
}


@dataclass
class RiskGoalImpact:
    """Impact of a single risk on a single goal."""
    risk_id: str
    goal_id: str
    impact_low: float
    impact_likely: float
    impact_high: float
    rationale: str


RISK_GOAL_IMPACTS: Dict[str, List[RiskGoalImpact]] = {
    # ═══════════════════════════════════════════════════════════
    # SKIPULAG OG LEYFI
    # ═══════════════════════════════════════════════════════════
    "R01": [
        RiskGoalImpact("R01", "G1", 3, 6, 12,
                        "Seinkun á deiliskipulagi bætir 3–12 mánuðum við innviðaáætlun"),
        RiskGoalImpact("R01", "G2", 3, 6, 12,
                        "Keðjuverkun: seinkun á innviðum seinkar byggingum"),
        RiskGoalImpact("R01", "G4", 50, 150, 400,
                        "Umsýslukostnaður og verðbólga á biðtíma (M kr.)"),
    ],
    "R02": [
        RiskGoalImpact("R02", "G1", 6, 12, 24,
                        "Kæra getur bætt 6–24 mánuðum við áætlun"),
        RiskGoalImpact("R02", "G2", 6, 12, 24,
                        "Keðjuverkun: kæra seinkar öllu"),
        RiskGoalImpact("R02", "G4", 100, 300, 800,
                        "Lögfræðikostnaður og tafakostnaður (M kr.)"),
        RiskGoalImpact("R02", "G5", -5, -15, -40,
                        "Kæra getur stöðvað verkefni (prósentustig)"),
        RiskGoalImpact("R02", "G9", -5, -10, -20,
                        "Kæra grefur undan ákvörðunarvaldi borgar"),
    ],
    "R03": [
        RiskGoalImpact("R03", "G2", 6, 12, 24,
                        "Endurskipulagning seinkar framkvæmdum"),
        RiskGoalImpact("R03", "G3", 5, 12, 25,
                        "Röng vara = verðmismunur (%)"),
        RiskGoalImpact("R03", "G5", -5, -15, -30,
                        "Óbyggilegt skipulag ógnar fullnaði"),
        RiskGoalImpact("R03", "G10", -5, -10, -20,
                        "Röng íbúðablöndun = félagsleg markmið bresta (prósentustig)"),
    ],
    "R04": [
        RiskGoalImpact("R04", "G1", 3, 8, 18,
                        "Breytingabeiðnir seinka innviðum"),
        RiskGoalImpact("R04", "G2", 4, 10, 24,
                        "Breytingar seinka byggingum enn meira"),
        RiskGoalImpact("R04", "G3", 3, 8, 15,
                        "Breytingar hækka kostnað sem skilar sér í verði (%)"),
        RiskGoalImpact("R04", "G5", -3, -10, -25,
                        "Endalausar breytingar ógna fullnaði"),
        # R04→G9 REMOVED: Change request probability is driven by F4 (integration),
        # not city governance factors. Kept S4 artificially high on City Control.
        RiskGoalImpact("R04", "G10", -3, -8, -15,
                        "Breytingar geta fjarlægt hagkvæmar íbúðir (prósentustig)"),
    ],
    "R05": [
        RiskGoalImpact("R05", "G1", 2, 4, 9,
                        "Umhverfismat dregst, seinkar innviðum"),
        RiskGoalImpact("R05", "G2", 2, 4, 9,
                        "Keðjuverkun á byggingar"),
    ],
    "R06": [
        RiskGoalImpact("R06", "G1", 2, 6, 18,
                        "Fornleifar geta seinkt framkvæmdum verulega"),
        RiskGoalImpact("R06", "G4", 50, 200, 800,
                        "Borgin greiðir fornleifarannsóknir á almenningsreit (M kr.)"),
    ],
    # ═══════════════════════════════════════════════════════════
    # INNVIÐIR (R07 merged into R10)
    # ═══════════════════════════════════════════════════════════
    "R08": [
        RiskGoalImpact("R08", "G4", 500, 2000, 6000,
                        "Beinn kostnaður borgar við innviði umfram áætlun (M kr.)"),
        RiskGoalImpact("R08", "G6", -15, -35, -60,
                        "Fjárhagsáætlun innviða springur (prósentustig)"),
    ],
    "R09": [
        RiskGoalImpact("R09", "G4", 200, 600, 2000,
                        "Viðhaldskostnaður til langframa vegna galla (M kr.)"),
        RiskGoalImpact("R09", "G6", -5, -10, -20,
                        "Viðgerðir fara úr fjárhagsáætlun (prósentustig)"),
        RiskGoalImpact("R09", "G7", -10, -25, -45,
                        "Gæðaeinkunn innviða lækkar"),
    ],
    "R10": [
        # Combined R10 (infra delays) + R07 (utility delays).
        # Utility delays (Veitur OR) are a common sub-cause.
        # Impact slightly raised to reflect combined scope.
        RiskGoalImpact("R10", "G1", 4, 10, 24,
                        "Innviða- og veitutafir seinka afhendingu beint"),
        RiskGoalImpact("R10", "G2", 4, 10, 24,
                        "Keðjuverkun: íbúðir geta ekki fólk fyrr en innviðir eru tilbúnir"),
        RiskGoalImpact("R10", "G6", -10, -15, -25,
                        "Tafir hækka innviðakostnað og þrýsta á fjárhagsáætlun"),
    ],
    # ═══════════════════════════════════════════════════════════
    # FRAMKVÆMDIR (R16 merged into R12)
    # ═══════════════════════════════════════════════════════════
    "R11": [
        RiskGoalImpact("R11", "G2", 12, 24, 48,
                        "Gjaldþrot stöðvar framkvæmdir í marga mánuði"),
        RiskGoalImpact("R11", "G5", -15, -35, -70,
                        "Fullnaður í alvarlegri hættu"),
        RiskGoalImpact("R11", "G8", -10, -20, -35,
                        "Verktakar í erfiðleikum draga úr gæðum"),
        # R11→G9 REMOVED: Bankruptcy probability is driven by F2 (contractor
        # strength) and F3 (capital patience), not city governance factors.
        # Kept S4 (F2=5) artificially high on City Control.
        RiskGoalImpact("R11", "G10", -10, -20, -30,
                        "Nýr eigandi byggir lúxus, ekki hagkvæmt"),
    ],
    "R12": [
        # Combined R12 (construction cost) + R16 (material prices).
        # Material price spikes are a major driver of construction
        # cost overruns, especially in Iceland where most materials
        # are imported.
        RiskGoalImpact("R12", "G2", 3, 8, 18,
                        "Kostnaðarvandamál hægja á framkvæmdum"),
        RiskGoalImpact("R12", "G3", 5, 12, 25,
                        "Kostnaðaraukning skilar sér beint í verði til kaupenda (%)"),
        RiskGoalImpact("R12", "G5", -5, -15, -35,
                        "Kostnaðarspírall ógnar framgangi verkefnis"),
        RiskGoalImpact("R12", "G10", -5, -12, -25,
                        "Hagkvæmar íbúðir verða óhagkvæmar þegar kostnaður hækkar"),
    ],
    "R13": [
        RiskGoalImpact("R13", "G2", 6, 12, 30,
                        "Beinar tafir á byggingum"),
    ],
    "R14": [
        RiskGoalImpact("R14", "G8", -10, -25, -45,
                        "Gæðaeinkunn bygginga lækkar"),
    ],
    "R15": [
        RiskGoalImpact("R15", "G2", 4, 10, 20,
                        "Mannekla seinkar framkvæmdum"),
        RiskGoalImpact("R15", "G8", -5, -12, -25,
                        "Flýtivinna = léleg gæði"),
    ],
    "R17": [
        RiskGoalImpact("R17", "G1", 3, 8, 18,
                        "Samhæfingarbrestur seinkar innviðum"),
        RiskGoalImpact("R17", "G2", 4, 10, 24,
                        "Tafir flæða yfir í byggingar"),
        RiskGoalImpact("R17", "G7", -5, -12, -25,
                        "Samhæfingargallar = gæðagallar í innviðum"),
        RiskGoalImpact("R17", "G8", -5, -12, -25,
                        "Samhæfingargallar = gæðagallar í byggingum"),
    ],
    # ═══════════════════════════════════════════════════════════
    # MARKAÐUR (R21 removed)
    # ═══════════════════════════════════════════════════════════
    "R18": [
        RiskGoalImpact("R18", "G2", 12, 24, 48,
                        "Verktakar hægja eða stöðva framkvæmdir í samdrætti"),
        RiskGoalImpact("R18", "G5", -10, -25, -50,
                        "Eftirspurnarbrestur ógnar fullnaði"),
    ],
    "R19": [
        RiskGoalImpact("R19", "G5", -10, -25, -50,
                        "Verktakar geta hætt þegar verð fer undir framkvæmdakostnað"),
    ],
    "R20": [
        RiskGoalImpact("R20", "G2", 6, 12, 30,
                        "Fjármögnunarþrýstingur hægir á öllu"),
        RiskGoalImpact("R20", "G3", 5, 12, 25,
                        "Fjármögnunarkostnaður skilar sér til kaupenda (%)"),
        RiskGoalImpact("R20", "G5", -8, -20, -45,
                        "Vaxtaskellur getur stöðvað verkefni"),
    ],
    # ═══════════════════════════════════════════════════════════
    # FJÁRMÖGNUN
    # ═══════════════════════════════════════════════════════════
    "R22": [
        RiskGoalImpact("R22", "G2", 12, 24, 48,
                        "Fjármögnunarbrestur stöðvar framkvæmdir"),
        RiskGoalImpact("R22", "G5", -15, -35, -60,
                        "Engin fjármögnun = ekkert verkefni"),
    ],
    "R23": [
        RiskGoalImpact("R23", "G2", 12, 24, 36,
                        "Sjóður hættir, alvarleg seinkun á meðan nýr fjárfestir finnst"),
        RiskGoalImpact("R23", "G5", -10, -25, -45,
                        "Helsti fjármögnunaraðili hverfur, ógnar framgangi"),
        RiskGoalImpact("R23", "G9", -10, -20, -35,
                        "Nýr aðili er ekki bundinn sömu skuldbindingum"),
    ],
    # ═══════════════════════════════════════════════════════════
    # STJÓRNMÁL OG SAMFÉLAG
    # ═══════════════════════════════════════════════════════════
    "R24": [
        RiskGoalImpact("R24", "G2", 6, 12, 24,
                        "Pólitísk óvissa seinkar ákvörðunum"),
        RiskGoalImpact("R24", "G5", -5, -15, -35,
                        "Nýr meirihluti getur breytt eða stöðvað verkefni"),
        RiskGoalImpact("R24", "G9", -10, -25, -45,
                        "Stefnubreyting breytir forsendum"),
        RiskGoalImpact("R24", "G10", -5, -15, -30,
                        "Nýjar áherslur geta dregið úr félagslegri blöndun"),
    ],
    "R25": [
        RiskGoalImpact("R25", "G1", 2, 6, 15,
                        "Nýjar kröfur valda endurvinnslu"),
        RiskGoalImpact("R25", "G2", 2, 6, 15,
                        "Keðjuverkun á byggingar"),
    ],
    "R26": [
        RiskGoalImpact("R26", "G1", 3, 8, 18,
                        "Andstaða seinkar samþykktum"),
        RiskGoalImpact("R26", "G2", 3, 8, 18,
                        "Keðjuverkun á byggingar"),
        RiskGoalImpact("R26", "G5", -3, -10, -25,
                        "Mikil andstaða getur stöðvað verkefni"),
        RiskGoalImpact("R26", "G9", -5, -15, -30,
                        "Pólitískur þrýstingur takmarkar valmöguleika borgar"),
    ],
    # ═══════════════════════════════════════════════════════════
    # VERKEFNISSTJÓRNUN OG SAMNINGAR (R28 merged into R27)
    # ═══════════════════════════════════════════════════════════
    "R27": [
        # Combined R27 (owner coordination) + R28 (contractual disputes).
        # G4 impact from R28 (legal costs) now included.
        RiskGoalImpact("R27", "G1", 4, 10, 24,
                        "Deilur eigenda og samningaágreiningur seinkar innviðum"),
        RiskGoalImpact("R27", "G2", 6, 15, 36,
                        "Deilur stöðva ákvarðanir og seinka öllu"),
        RiskGoalImpact("R27", "G4", 100, 400, 1200,
                        "Lögfræðikostnaður og sáttir (M kr.)"),
        RiskGoalImpact("R27", "G5", -5, -15, -35,
                        "Stjórnunarbrestur ógnar framgangi"),
        RiskGoalImpact("R27", "G9", -10, -25, -45,
                        "Borgin missir áhrif í deilum"),
    ],
    # ═══════════════════════════════════════════════════════════
    # NEW RISKS
    # ═══════════════════════════════════════════════════════════
    "R29": [
        RiskGoalImpact("R29", "G4", 100, 400, 1500,
                        "Viðgerðir og ábyrgðamál árum eftir afhendingu (M kr.)"),
        RiskGoalImpact("R29", "G7", -5, -15, -30,
                        "Gallar draga úr upplifun og nothæfi innviða"),
        RiskGoalImpact("R29", "G8", -5, -15, -30,
                        "Gallar í byggingum koma í ljós árum síðar"),
    ],
    "R30": [
        RiskGoalImpact("R30", "G3", 5, 15, 30,
                        "Virðisaukning lands skilar sér í hærra íbúðaverði (%)"),
        # v5: G4 added — city loses money when intermediary captures land value
        RiskGoalImpact("R30", "G4", 200, 800, 2000,
                        "Borgin selur réttindi undir markaðsverði eða missir millisöluálag (M kr.)"),
        RiskGoalImpact("R30", "G9", -10, -25, -45,
                        "Borgin er bundin samningi þar sem hún hefur gefið eftir of mikið"),
        RiskGoalImpact("R30", "G10", -5, -15, -30,
                        "Of veik skilyrði gera félagslega blöndun óframkvæmanlega"),
    ],
    "R31": [
        RiskGoalImpact("R31", "G1", 4, 10, 24,
                        "Áfangar samræmast ekki, innviðir liggja ónotaðir"),
        RiskGoalImpact("R31", "G2", 6, 15, 36,
                        "Áfangi 2 stöðvast ef áfangi 1 gengur illa"),
        RiskGoalImpact("R31", "G4", 200, 800, 3000,
                        "Ónotaðir innviðir og tvíverknaður kosta borgina (M kr.)"),
        RiskGoalImpact("R31", "G5", -5, -15, -40,
                        "Hálflokið svæði sem enginn vill klára"),
    ],
    "R32": [
        RiskGoalImpact("R32", "G5", -3, -10, -20,
                        "Veik eftirlit dregur úr líkum á fullnaði"),
        RiskGoalImpact("R32", "G7", -5, -12, -25,
                        "Ónóg eftirlit dregur úr gæðum innviða"),
        RiskGoalImpact("R32", "G9", -5, -15, -30,
                        "Borgin getur ekki framfylgt markmiðum ef hún vantar sérfræðinga"),
    ],
    "R33": [
        RiskGoalImpact("R33", "G10", -5, -15, -30,
                        "Félagsleg blöndun nást ekki þrátt fyrir samningsskuldbindingu"),
    ],
    # ═══════════════════════════════════════════════════════════
    # v5 ADDITIONS
    # ═══════════════════════════════════════════════════════════
    "R34": [
        RiskGoalImpact("R34", "G2", 2, 6, 14,
                        "Skattaleg skipulagning tekur tíma og getur stöðvað framkvæmdir (mán.)"),
        RiskGoalImpact("R34", "G4", 200, 600, 1500,
                        "Skattkostnaður, endurskipulagning, ráðgjöf, hugsanleg sektir (M kr.)"),
        RiskGoalImpact("R34", "G9", -5, -10, -20,
                        "Pólitísk áhætta ef skattavandamál verða opinber"),
    ],
    "R35": [
        RiskGoalImpact("R35", "G1", 2, 6, 12,
                        "Lögboðnir útboðsferlar seinka innviðaframkvæmdum (mán.)"),
        RiskGoalImpact("R35", "G2", 3, 8, 18,
                        "Útboð, kærufrestur og biðtími seinka byggingum (mán.)"),
        RiskGoalImpact("R35", "G5", -3, -8, -15,
                        "Stífir ferlar geta stöðvað verkefni ef útboð mistekst (prósentustig)"),
    ],
    "R36": [
        RiskGoalImpact("R36", "G2", 3, 8, 18,
                        "Slit samstarfs stöðvar framkvæmdir (mán.)"),
        RiskGoalImpact("R36", "G4", 100, 400, 1200,
                        "Lögfræðikostnaður, uppgjör, eignasala undir verði (M kr.)"),
        RiskGoalImpact("R36", "G5", -5, -12, -25,
                        "Hætta á að verkefni klárast ekki ef samstarf brotnar (prósentustig)"),
        RiskGoalImpact("R36", "G9", -5, -15, -30,
                        "Borgin missir samningsstöðu í slitaviðræðum"),
    ],
    "R37": [
        RiskGoalImpact("R37", "G1", 2, 5, 12,
                        "Kærur vegna hagsmunaárekstra seinka skipulagsákvörðunum (mán.)"),
        RiskGoalImpact("R37", "G2", 2, 5, 12,
                        "Ný útboð eða ógildingar seinka byggingum (mán.)"),
        RiskGoalImpact("R37", "G5", -3, -8, -18,
                        "Endurtekin ógildingar ógna fullnaði (prósentustig)"),
        RiskGoalImpact("R37", "G9", -5, -15, -30,
                        "Trúverðugleiki borgar sem skipulagsyfirvalds dregst í efa"),
    ],
}


def get_impacts_for_risk(risk_id: str) -> List[RiskGoalImpact]:
    """Get all goal impacts for a risk."""
    return RISK_GOAL_IMPACTS.get(risk_id, [])


def get_impacts_for_goal(goal_id: str) -> List[RiskGoalImpact]:
    """Get all risk impacts affecting a goal."""
    result = []
    for risk_id, impacts in RISK_GOAL_IMPACTS.items():
        for impact in impacts:
            if impact.goal_id == goal_id:
                result.append(impact)
    return result


def pert_mean(low: float, likely: float, high: float) -> float:
    """Calculate PERT weighted mean."""
    return (low + 4 * likely + high) / 6