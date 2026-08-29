from pathlib import Path

from helpers import default_index_parser

from conlanger.tools.ingest.flatten_nested_sets import flatten_nested_sets

_INDEX_DIACHRONICA_HTML = """\
<!doctype html>
<html><head><meta charset="utf-8"></head><body>
<section id="{section_id}">
{section_body}
</section>
</body></html>
"""


def _write_index_html(path: Path, *, section_id: str, section_body: str) -> None:
    path.write_text(
        _INDEX_DIACHRONICA_HTML.format(
            section_id=section_id,
            section_body=section_body,
        ),
        encoding="utf-8",
    )


def test_flatten_nested_sets_unions_inner_members():
    assert flatten_nested_sets("{a,{b,c}}") == "{a,b,c}"


def test_flatten_nested_sets_distributes_suffix_over_inner_set():
    assert flatten_nested_sets("{{h,k,ŋ}n,w,v,l,r}_") == "{hn,kn,ŋn,w,v,l,r}_"


def test_flatten_nested_sets_expands_parenthetical_in_set():
    assert flatten_nested_sets("_{s,({m,j,w})V}") == "_{s,mV,jV,wV}"
    assert flatten_nested_sets("_ə{(C){p,kʷ},m,w}") == "_ə{(C)p,(C)kʷ,m,w}"


def test_flatten_nested_sets_leaves_unbalanced_and_parallel_columns():
    unbalanced = "e o u æ ø y → {a,e} {o,u} {a,o,u a {a,o,u} {o,u,i}"
    assert flatten_nested_sets(unbalanced) == unbalanced
    assert flatten_nested_sets("(h)ə{p,b}") == "(h)ə{p,b}"


def test_flatten_nested_sets_leaves_field_level_paren_wrapped_flat_set():
    assert flatten_nested_sets("V[+nas]({ʔ,s})w_") == "V[+nas]({ʔ,s})w_"
    assert flatten_nested_sets("({p,t,k})n") == "({p,t,k})n"


def test_flatten_nested_sets_flattens_feature_matrix_labialization_cluster():
    assert (
        flatten_nested_sets("{{C[-fr,+bk,-hi,-lo],K}ʷ,w}_")
        == "{C[-fr,+bk,-hi,-lo]ʷ,Kʷ,w}_"
    )


def test_flatten_nested_sets_does_not_reserialize_flat_env_sets():
    assert flatten_nested_sets(":{#_, _#}:") == ":{#_, _#}:"
    assert flatten_nested_sets("{a, b, c}") == "{a, b, c}"


def test_parse_flattens_nested_env_munsee_delaware(tmp_path: Path):
    html_path = tmp_path / "index.html"
    _write_index_html(
        html_path,
        section_id="Munsee",
        section_body="""\
<h2>1.0 Munsee</h2>
<p class="schg" id="Munsee-Delaware-Cʷ">Cʷ → C / _ə{(C){p,kʷ},m,w}</p>
""",
    )
    rule = default_index_parser().parse(html_path)["sections"][0]["rules"][0]
    assert rule["env"] == "_ə{(C)p,(C)kʷ,m,w}"
    assert rule["raw"] == "Cʷ → C / _ə{(C){p,kʷ},m,w}"


def test_parse_flattens_nested_env_and_else_copied_exception(tmp_path: Path):
    html_path = tmp_path / "index.html"
    _write_index_html(
        html_path,
        section_id="Old-Irish",
        section_body="""\
<h2>17.5.1 Proto-Indo-European to Old Irish</h2>
<p class="schg" id="Old-Irish-m̩-n̩">m̩ n̩ → am an / _{s,({m,j,w})V}</p>
<p class="schg" id="Old-Irish-m̩-n̩_2">m̩ n̩ → em en / else</p>
""",
    )
    rules = default_index_parser().parse(
        html_path,
        source_file="index_diachronica_original.html",
    )["sections"][0]["rules"]
    assert rules[0]["env"] == "_{s,mV,jV,wV}"
    assert rules[1]["exception"] == "_{s,mV,jV,wV}"
    assert rules[0]["raw"] == "m̩ n̩ → am an / _{s,({m,j,w})V}"
    assert rules[1]["raw"] == "m̩ n̩ → em en / else"


def test_parse_flattens_nested_exception_old_norse(tmp_path: Path):
    html_path = tmp_path / "index.html"
    _write_index_html(
        html_path,
        section_id="Old-Norse",
        section_body="""\
<h2>1.0 Old Norse</h2>
<p class="schg" id="Old-Norse-e_2">e → ja / ! {{h,k,ŋ}n,w,v,l,r}_, _{u,o,i}</p>
""",
    )
    rule = default_index_parser().parse(html_path)["sections"][0]["rules"][0]
    assert rule["exception"] == "{hn,kn,ŋn,w,v,l,r}_, _{u,o,i}"
    assert rule["raw"] == "e → ja / ! {{h,k,ŋ}n,w,v,l,r}_, _{u,o,i}"


def test_parse_flattens_deferred_else_prev_exception_in_place(tmp_path: Path):
    html_path = tmp_path / "index.html"
    _write_index_html(
        html_path,
        section_id="Blackfoot",
        section_body="""\
<h2>1.0 Blackfoot</h2>
<p class="schg" id="Blackfoot-aː">aː → aa / W_ ! when _{C{C,ː},#}</p>
<p class="schg" id="Blackfoot-aː_2">aː → a / else</p>
""",
    )
    rules = default_index_parser().parse(html_path)["sections"][0]["rules"]
    assert rules[0]["exception"] == "when _{CC,Cː,#}"
    assert rules[1]["env"] == "else"
    assert rules[0]["raw"] == "aː → aa / W_ ! when _{C{C,ː},#}"


def test_parse_flattens_nested_env_nooksack(tmp_path: Path):
    html_path = tmp_path / "index.html"
    _write_index_html(
        html_path,
        section_id="Nooksack",
        section_body="""\
<h2>1.0 Nooksack</h2>
<p class="schg" id="Nooksack-s_2">s → ʃ / #_{xʲ,w{i,a},qʷa}</p>
""",
    )
    rule = default_index_parser().parse(html_path)["sections"][0]["rules"][0]
    assert rule["env"] == "#_{xʲ,wi,wa,qʷa}"
    assert rule["raw"] == "s → ʃ / #_{xʲ,w{i,a},qʷa}"


def test_parse_flattens_nested_stages_common_anatolian(tmp_path: Path):
    html_path = tmp_path / "index.html"
    _write_index_html(
        html_path,
        section_id="Common-Anatolian",
        section_body="""\
<h2>17.2 Proto-Indo-European to Common Anatolian</h2>
<p class="schg">{{h₁,h₃}s,s{h₁,h₃}} → sː</p>
""",
    )
    rule = default_index_parser().parse(html_path)["sections"][0]["rules"][0]
    assert rule["stages"][0] == "{h₁s,h₃s,sh₁,sh₃}"
    assert rule["raw"] == "{{h₁,h₃}s,s{h₁,h₃}} → sː"


def test_parse_flattens_nested_stages_old_norse(tmp_path: Path):
    html_path = tmp_path / "index.html"
    _write_index_html(
        html_path,
        section_id="Old-Norse",
        section_body="""\
<h2>1.0 Old Norse</h2>
<p class="schg">a(i) {e,w{æ,i}} {we,ei} (w)ɪ → ey ø y ʏ / w_ ! hw_</p>
""",
    )
    rule = default_index_parser().parse(html_path)["sections"][0]["rules"][0]
    assert rule["stages"][0] == "a(i) {e,wæ,wi} {we,ei} (w)ɪ"
    assert rule["raw"] == "a(i) {e,w{æ,i}} {we,ei} (w)ɪ → ey ø y ʏ / w_ ! hw_"


def test_parse_flattens_nested_stages_egyptian_arabic(tmp_path: Path):
    html_path = tmp_path / "index.html"
    _write_index_html(
        html_path,
        section_id="Egyptian-Arabic",
        section_body="""\
<h2>1.0 Egyptian Arabic</h2>
<p class="schg">{{s,z}(ˤ),ʒ}ʃ → ʃː</p>
""",
    )
    rule = default_index_parser().parse(html_path)["sections"][0]["rules"][0]
    assert rule["stages"][0] == "{s(ˤ),z(ˤ),ʒ}ʃ"
    assert rule["raw"] == "{{s,z}(ˤ),ʒ}ʃ → ʃː"


def test_parse_leaves_bucket_d_stage_shapes_unchanged(tmp_path: Path):
    html_path = tmp_path / "index.html"
    _write_index_html(
        html_path,
        section_id="Muong-Khen",
        section_body="""\
<h2>1.0 Muong Khen</h2>
<p class="schg">(h)ə{p,b} → t / _l</p>
<p class="schg">e(C){V[- low]} e(C)a → e(C) e(C)ə</p>
<p class="schg">a(C){o,e} → a</p>
""",
    )
    rules = default_index_parser().parse(html_path)["sections"][0]["rules"]
    assert rules[0]["stages"][0] == "(h)ə{p,b}"
    assert rules[1]["stages"][0] == "e(C){V[- low]} e(C)a"
    assert rules[2]["stages"][0] == "a(C){o,e}"


def test_parse_leaves_compile_created_nesting_unchanged(tmp_path: Path):
    html_path = tmp_path / "index.html"
    _write_index_html(
        html_path,
        section_id="Aari",
        section_body="""\
<h2>1.0 Aari</h2>
<p class="schg">{x₁,x₂} → ɡ</p>
""",
    )
    rule = default_index_parser().parse(html_path)["sections"][0]["rules"][0]
    assert rule["stages"][0] == "{x₁,x₂}"
