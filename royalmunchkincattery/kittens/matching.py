"""Kitten Match: scores available kittens against a visitor's answers.

Transparent on purpose: every criterion has a fixed weight, so the percentage
shown to the visitor is just "points earned / points possible".
"""

from .models import Kitten

WEIGHTS = {
    "coat": 20,
    "energy": 30,
    "kids": 15,
    "pets": 15,
    "gender": 10,
    "budget": 10,
}


def score_kitten(kitten, answers):
    earned = possible = 0
    reasons = []

    coat = answers.get("coat")
    if coat in ("shorthair", "longhair"):
        possible += WEIGHTS["coat"]
        if kitten.coat_length == coat:
            earned += WEIGHTS["coat"]
            reasons.append(f"{kitten.get_coat_length_display()} coat, as you wanted")

    energy = answers.get("energy")
    if energy in dict(Kitten.Energy.choices) and kitten.energy != Kitten.Energy.UNCONFIRMED:
        possible += WEIGHTS["energy"]
        if kitten.energy == energy:
            earned += WEIGHTS["energy"]
            reasons.append(f"{kitten.get_energy_display().lower()} personality")
        elif {kitten.energy, energy} == {"playful", "adventurous"} or {kitten.energy, energy} == {"playful", "calm"}:
            earned += WEIGHTS["energy"] // 2

    if answers.get("kids") == "yes" and kitten.care_info_confirmed:
        possible += WEIGHTS["kids"]
        if kitten.good_with_kids:
            earned += WEIGHTS["kids"]
            reasons.append("good with children")

    if answers.get("pets") == "yes" and kitten.care_info_confirmed:
        possible += WEIGHTS["pets"]
        if kitten.good_with_pets:
            earned += WEIGHTS["pets"]
            reasons.append("good with other pets")

    gender = answers.get("gender")
    if gender in ("male", "female"):
        possible += WEIGHTS["gender"]
        if kitten.gender == gender:
            earned += WEIGHTS["gender"]
            reasons.append(f"{kitten.get_gender_display().lower()}, as you wanted")

    budget = answers.get("budget")
    if budget:
        possible += WEIGHTS["budget"]
        if kitten.price <= budget:
            earned += WEIGHTS["budget"]
            reasons.append("within your budget")

    percent = round(100 * earned / possible) if possible else 0
    return percent, reasons


def best_matches(queryset, answers, limit=3):
    scored = []
    for kitten in queryset:
        percent, reasons = score_kitten(kitten, answers)
        scored.append((percent, kitten, reasons))
    scored.sort(key=lambda t: (-t[0], t[1].price, t[1].name))
    return [{"percent": p, "kitten": k, "reasons": r} for p, k, r in scored[:limit]]
