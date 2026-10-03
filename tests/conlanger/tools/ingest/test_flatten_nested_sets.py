import pytest
from lxml import html

from conlanger.tools.ingest import IndexDiachronicaParser
from conlanger.tools.ingest.flatten_nested_sets import (
    _consume_segment_tail,
    _try_distribute,
    flatten_nested_sets,
)


def _parse_section_html(section_id: str, section_body: str) -> list[dict]:
    root = html.document_fromstring(f"""\
<!doctype html><html><body><section id="{section_id}">
{section_body}
</section></body></html>""")
    return IndexDiachronicaParser().parse(root)["sections"]


@pytest.mark.parametrize(
    "input,expected",
    [
        pytest.param("{a,{b,c}}", "{a,b,c}", id="unions_inner_member"),
        pytest.param(
            "{{h,k,ŋ}n,w,v,l,r}_",
            "{hn,kn,ŋn,w,v,l,r}_",
            id="distributes_suffix_over_inner_set",
        ),
        pytest.param(
            "_{s,({m,j,w})V}",
            "_{s,mV,jV,wV}",
            id="expands_parenthetical_1",
        ),
        pytest.param(
            "_ə{(C){p,kʷ},m,w}",
            "_ə{(C)p,(C)kʷ,m,w}",
            id="expands_parenthetical_2",
        ),
        pytest.param(
            "{x,({a,b})V}",
            "{x,aV,bV}",
            id="expands_parenthetical_3",
        ),
        pytest.param(
            "{x,({a,b})[+voice]}",
            "{x,a[+voice],b[+voice]}",
            id="expands_parenthetical_4",
        ),
        pytest.param(
            "e o u æ ø y → {a,e} {o,u} {a,o,u a {a,o,u} {o,u,i}",
            "e o u æ ø y → {a,e} {o,u} {a,o,u a {a,o,u} {o,u,i}",
            id="leaves_unbalanced_1",
        ),
        pytest.param(
            "}{a,b}",
            "}{a,b}",
            id="leaves_unbalanced_2",
        ),
        pytest.param(
            "(h)ə{p,b}",
            "(h)ə{p,b}",
            id="leaves_parallel_columns",
        ),
        pytest.param(
            "V[+nas]({ʔ,s})w_",
            "V[+nas]({ʔ,s})w_",
            id="leaves_paren_wrapped_flat_set_1",
        ),
        pytest.param(
            "({p,t,k})n",
            "({p,t,k})n",
            id="leaves_paren_wrapped_flat_set_2",
        ),
        pytest.param(
            "{{C[-fr,+bk,-hi,-lo],K}ʷ,w}_",
            "{C[-fr,+bk,-hi,-lo]ʷ,Kʷ,w}_",
            id="flattens_with_diacritic_marks_applied_to_sets",
        ),
        pytest.param(
            "#_, _#",
            "#_, _#",
            id="leaves_flat_env_sets",
        ),
        pytest.param(
            "{a, b, c}",
            "{a, b, c}",
            id="leaves_flat_sets",
        ),
        pytest.param(
            "{({a,b})}",
            "{a,b}",
            id="flattens_paren_only_set_member",
        ),
    ],
)
def test_flatten_nested_sets(input, expected):
    assert flatten_nested_sets(input) == expected


@pytest.mark.parametrize(
    ("member", "expected"),
    [
        ("({a,b})V", ["aV", "bV"]),
        ("{a,b}", None),
        ("x{}y", None),
    ],
)
def test_try_distribute_paren_wrapped_and_guard_paths(member, expected):
    assert _try_distribute(member) == expected


@pytest.mark.parametrize(
    ("text", "start", "expected_end"),
    [
        ("a[+voice", 1, 1),
        ("a(C)", 1, 1),
    ],
)
def test_consume_segment_tail_stops_on_unclosed_or_nested_groupers(
    text, start, expected_end
):
    assert _consume_segment_tail(text, start) == expected_end


def test_parse_flattens_nested_env_munsee_delaware():
    rule = _parse_section_html(
        "Munsee",
        """\
<h2>1.0 Munsee</h2>
<p class="schg" id="Munsee-Delaware-Cʷ">Cʷ → C / _ə{(C){p,kʷ},m,w}</p>
""",
    )[0]["rules"][0]
    assert rule["env"] == "_ə{(C)p,(C)kʷ,m,w}"
    assert rule["raw"] == "Cʷ → C / _ə{(C){p,kʷ},m,w}"


def test_parse_flattens_nested_env_and_else_copied_exception():
    rules = _parse_section_html(
        "Old-Irish",
        """\
<h2>17.5.1 Proto-Indo-European to Old Irish</h2>
<p class="schg" id="Old-Irish-m̩-n̩">m̩ n̩ → am an / _{s,({m,j,w})V}</p>
<p class="schg" id="Old-Irish-m̩-n̩_2">m̩ n̩ → em en / else</p>
""",
    )[0]["rules"]
    assert rules[0]["env"] == "_{s,mV,jV,wV}"
    assert rules[1]["exception"] == "_{s,mV,jV,wV}"
    assert rules[0]["raw"] == "m̩ n̩ → am an / _{s,({m,j,w})V}"
    assert rules[1]["raw"] == "m̩ n̩ → em en / else"


def test_parse_flattens_nested_exception_old_norse():
    rule = _parse_section_html(
        "Old-Norse",
        """\
<h2>1.0 Old Norse</h2>
<p class="schg" id="Old-Norse-e_2">e → ja / ! {{h,k,ŋ}n,w,v,l,r}_, _{u,o,i}</p>
""",
    )[0]["rules"][0]
    assert rule["exception"] == "{hn,kn,ŋn,w,v,l,r}_, _{u,o,i}"
    assert rule["raw"] == "e → ja / ! {{h,k,ŋ}n,w,v,l,r}_, _{u,o,i}"


def test_parse_flattens_deferred_else_prev_exception_in_place():
    rules = _parse_section_html(
        "Blackfoot",
        """\
<h2>1.0 Blackfoot</h2>
<p class="schg" id="Blackfoot-aː">aː → aa / W_ ! when _{C{C,ː},#}</p>
<p class="schg" id="Blackfoot-aː_2">aː → a / else</p>
""",
    )[0]["rules"]
    assert rules[0]["exception"] == "when _{CC,Cː,#}"
    assert rules[1]["env"] == "else"
    assert rules[0]["raw"] == "aː → aa / W_ ! when _{C{C,ː},#}"


def test_parse_flattens_nested_env_nooksack():
    rule = _parse_section_html(
        "Nooksack",
        """\
<h2>1.0 Nooksack</h2>
<p class="schg" id="Nooksack-s_2">s → ʃ / #_{xʲ,w{i,a},qʷa}</p>
""",
    )[0]["rules"][0]
    assert rule["env"] == "#_{xʲ,wi,wa,qʷa}"
    assert rule["raw"] == "s → ʃ / #_{xʲ,w{i,a},qʷa}"


def test_parse_flattens_nested_stages_common_anatolian():
    rule = _parse_section_html(
        "Common-Anatolian",
        """\
<h2>17.2 Proto-Indo-European to Common Anatolian</h2>
<p class="schg">{{h₁,h₃}s,s{h₁,h₃}} → sː</p>
""",
    )[0]["rules"][0]
    assert rule["stages"][0] == "{h₁s,h₃s,sh₁,sh₃}"
    assert rule["raw"] == "{{h₁,h₃}s,s{h₁,h₃}} → sː"


def test_parse_flattens_nested_stages_old_norse():
    rule = _parse_section_html(
        "Old-Norse",
        """\
<h2>1.0 Old Norse</h2>
<p class="schg">a(i) {e,w{æ,i}} {we,ei} (w)ɪ → ey ø y ʏ / w_ ! hw_</p>
""",
    )[0]["rules"][0]
    assert rule["stages"][0] == "a(i) {e,wæ,wi} {we,ei} (w)ɪ"
    assert rule["raw"] == "a(i) {e,w{æ,i}} {we,ei} (w)ɪ → ey ø y ʏ / w_ ! hw_"


def test_parse_flattens_nested_stages_egyptian_arabic():
    rule = _parse_section_html(
        "Egyptian-Arabic",
        """\
<h2>1.0 Egyptian Arabic</h2>
<p class="schg">{{s,z}(ˤ),ʒ}ʃ → ʃː</p>
""",
    )[0]["rules"][0]
    assert rule["stages"][0] == "{s(ˤ),z(ˤ),ʒ}ʃ"
    assert rule["raw"] == "{{s,z}(ˤ),ʒ}ʃ → ʃː"


def test_parse_leaves_bucket_d_stage_shapes_unchanged():
    rules = _parse_section_html(
        "Muong-Khen",
        """\
<h2>1.0 Muong Khen</h2>
<p class="schg">(h)ə{p,b} → t / _l</p>
<p class="schg">e(C){V[- low]} e(C)a → e(C) e(C)ə</p>
<p class="schg">a(C){o,e} → a</p>
""",
    )[0]["rules"]
    assert rules[0]["stages"][0] == "(h)ə{p,b}"
    assert rules[1]["stages"][0] == "e(C){V[- low]} e(C)a"
    assert rules[2]["stages"][0] == "a(C){o,e}"


def test_parse_leaves_compile_created_nesting_unchanged():
    rule = _parse_section_html(
        "Aari",
        """\
<h2>1.0 Aari</h2>
<p class="schg">{x₁,x₂} → ɡ</p>
""",
    )[0]["rules"][0]
    assert rule["stages"][0] == "{x₁,x₂}"
