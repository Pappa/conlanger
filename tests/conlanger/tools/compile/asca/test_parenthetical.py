"""Tests for Index parenthetical segment notation (ticket 48)."""

import pytest

from conlanger.tools.compile.asca.parenthetical import (
    expand_index_parenthetical_notation,
)
from conlanger.appliers.asca import validate_asca
from conlanger.tools.rules import SoundChangeRuleSet


@pytest.mark.parametrize(
    ("index_rule", "expected"),
    [
        ("ɡ(ʷ)", "{ɡ,ɡʷ}"),
        ("b(ʷ)", "{b,bʷ}"),
        ("k(ʼ)", "{k:[+cg],k}"),
        ("t(ʰ?)", "{t,tʰ}"),
        ("e:[+long](ʲ)", "{e:[+long],eʲ:[+long]}"),
        ("ts:[+cg](ʷ)", "{ts:[+cg],ts:[+cg,+round]}"),
        ("{(t)l,θ}", "{tl,l,θ}"),
        ("{(d)l,f3}", "{dl,l,f3}"),
        ("{k(ʼ),q}", "{k:[+cg],k,q}"),
        ("{k(ʷ)es,keθ}", "{kes,kʷes,keθ}"),
        ("{r(ʲ),l(ʲ)}", "{r,rʲ,l,lʲ}"),
        ("(v)w", "{vw,w}"),
        ("o(ji)", "{o,oji}"),
        ("{p,z,d(r)}", "{p,z,d,dr}"),
        ("{p(ʷ),v}Vh", "{p,pʷ,v}Vh"),
        ("q > χ (> ʕ)", "q > χ"),
        ("ket > t:[+long] (> s:[+long]?)", "ket > t:[+long]"),
        ("{bl,tl} > ʈ (?)", "{bl,tl} > ʈ"),
        ("{ɡ,q}(?)", "{ɡ,q}"),
        ("z dz ɡ > ɡ {z,dz} ɡ(ʷ)", "z dz ɡ > ɡ {z,dz} {ɡ,ɡʷ}"),
        ("a > o / #Cw_{(d)l,f3}", "a > o / #Cw_{dl,l,f3}"),
        (
            "e o > i u / #{k(ʼ),x}_{t(ʼ),ts:[+cg]}",
            "e o > i u / #{k:[+cg],k,x}_{t:[+cg],t,ts:[+cg]}",
        ),
        ("y > i / {r(ʲ),l(ʲ)}_e", "y > i / {r,rʲ,l,lʲ}_e"),
        ("tʰ > d / #_(V){lʲ,r(ʲ)}", "tʰ > d / #_(V){lʲ,r,rʲ}"),
        ("e > i / #{s,ʃ,ts:[+cg]}_{k(w),ʔ}", "e > i / #{s,ʃ,ts:[+cg]}_{k,kʷ,ʔ}"),
        ("V[+ high] > ∅ / _# // {p,z,d(r)}_", "V[+ high] > ∅ / _# // {p,z,d,dr}_"),
    ],
)
def test_expand_index_parenthetical_notation(index_rule, expected):
    assert expand_index_parenthetical_notation(index_rule) == expected


def test_expand_index_parenthetical_notation_leaves_asca_env_optionals():
    assert expand_index_parenthetical_notation("C > V / (C,V)_") == "C > V / (C,V)_"
    assert expand_index_parenthetical_notation("C > V / (C,0)_") == "C > V / (C,0)_"


def test_expand_index_parenthetical_notation_leaves_bracket_matrices_untouched():
    assert expand_index_parenthetical_notation("C > V / [+high]") == "C > V / [+high]"


@pytest.mark.parametrize(
    ("inp", "out", "env"),
    [
        ("z dz ɡ", "ɡ {z,dz} ɡ(ʷ)", None),
        ("{(t)l,θ}", "t", None),
        ("aj aw", "e:[+long](ʲ) o:[+long](ʷ)", None),
        ("{bl,tl}", "ʈ", None),
        ("p pw t̪ ʈ c", "v (v)w r l j", "V_V"),
        ("y", "i", "{r(ʲ),l(ʲ)}_e"),
        ("a", "o", "#Cw_{(d)l,f3}"),
        ("e o", "i u", "#{k(ʼ),x}_{t(ʼ),ts:[+cg]}"),
        ("q", "χ", None),
        ("ket", "t:[+long]", None),
        ("χʷ", "x(ʷ)", None),
        ("tɬ tɬ:[+long] tɬ:[+cg] tɬ:[+long,+cg] dɮ", "xʲ {ɣʲ,ɡ} q:[+cg] k(ʼ)", None),
        ("{k(ʷ)es,keθ}", "s:[+long]", None),
        ("V[+ high]", "∅", "_# // {p,z,d(r)}_"),
    ],
)
def test_parenthetical_inventory_representatives_validate(inp, out, env):
    rule = {"stages": [inp, out]}
    if env is not None:
        rule["env"] = env
    section = {"index": "1", "section": "paren", "rules": [rule]}
    validate_asca(SoundChangeRuleSet(section, "asca"))
