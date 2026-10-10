from pathlib import Path
p=Path(__file__).parent
def test_synthesis_script_has_all_four_prior_phases():
 s=(p/"synthesize.py").read_text()
 for term in ["phase96","phase97","phase98","phase99","paper_rows","MANUSCRIPT.md","SUPPLEMENTARY_MATERIALS.md"]:
  assert term in s
def test_fixed_corpus_size_is_fourteen():
 s=(p/"synthesize.py").read_text()
 assert '("U14",' in s and '("U01",' in s
