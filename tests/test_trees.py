import importlib.util
import tempfile
import unittest
from pathlib import Path

from itol_cli.core import ItolError, annotate
from itol_cli.trees import convert_tree, inspect_tree, validate_ids, check_newick


@unittest.skipUnless(importlib.util.find_spec("Bio"), "Install trees extra for parser tests")
class TreeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)

    def tree(self, text, name="example.treefile"):
        path = self.path / name
        path.write_text(text)
        return path

    def test_treefile_and_support(self):
        result = inspect_tree(self.tree("((A:0.1,B:0.2)95:0.3,C:0.4)Root;"))
        self.assertEqual(result["format"], "newick")
        self.assertEqual(result["trees"][0]["tips"], 3)
        self.assertEqual(result["trees"][0]["internal_ids"], ["Root"])

    def test_quoted_names_and_nhx(self):
        result = inspect_tree(self.tree("('A species':0.1,B:0.2)[&&NHX:name=ROOT];"))
        self.assertIn("A species", result["trees"][0]["tip_ids"])
        self.assertEqual(result["trees"][0]["internal_ids"], ["ROOT"])

    def test_nexus_translate(self):
        result = inspect_tree(self.tree("#NEXUS\nBEGIN TREES;\nTRANSLATE 1 Alpha, 2 Beta;\nTREE T = (1:0.1,2:0.2);\nEND;"))
        self.assertEqual(result["format"], "nexus")
        self.assertEqual(result["trees"][0]["tip_ids"], ["Alpha", "Beta"])

    def test_roundtrip_formats(self):
        original = self.tree("((A:0.123456789,B:0.2)Node:0.3,C:0.4)Root;")
        for fmt in ("newick", "nexus", "phyloxml"):
            with self.subTest(fmt=fmt):
                data, report = convert_tree(original, fmt)
                target = self.path / ("converted." + fmt)
                target.write_bytes(data)
                result = inspect_tree(target)
                self.assertEqual(result["trees"][0]["tip_ids"], ["A", "B", "C"])
                self.assertEqual(result["trees"][0]["internal_ids"], ["Root", "Node"])
                self.assertTrue(report["warnings"])

    def test_multiple_trees_index(self):
        path = self.tree("(A,B);\n(C,D);")
        self.assertEqual(inspect_tree(path)["tree_count"], 2)
        data, report = convert_tree(path, "newick", index=1)
        self.assertIn(b"C", data)
        self.assertEqual(report["tree_count"], 1)
        with self.assertRaises(ItolError):
            convert_tree(path, "newick", index=-1)

    def test_invalid_newick(self):
        for value in ["(A,B)", "((A,B);", "(A:bad,B);", "(A:,B);", "('A,B);", "(A,B)[oops;"]:
            with self.subTest(value=value), self.assertRaises(ItolError):
                inspect_tree(self.tree(value))

    def test_duplicate_and_missing_tips(self):
        path = self.tree("(A,A);")
        self.assertEqual(inspect_tree(path)["trees"][0]["duplicate_ids"], ["A"])
        with self.assertRaises(ItolError):
            validate_ids(path, b"LABELS\nSEPARATOR TAB\nDATA\nA\tAlpha\n")

    def test_validation_direct_and_lca(self):
        path = self.tree("((A,B)Node,C)Root;")
        report = validate_ids(path, b"LABELS\nSEPARATOR TAB\nDATA\nA\tAlpha\nA|B\tClade\nA---C\tAll\nNode\tN\n")
        self.assertEqual(report["matched_rows"], 4)
        for node in ("Missing", "A|Missing", "CONTAINS==A"):
            with self.subTest(node=node), self.assertRaises(ItolError):
                validate_ids(path, ("LABELS\nSEPARATOR TAB\nDATA\n" + node + "\tLabel\n").encode())

    def test_unsupported_qza_and_jplace(self):
        for text, name in [("zip", "test.qza"), ('{"tree": "(A,B);"}', "test.jplace")]:
            with self.assertRaises(ItolError):
                inspect_tree(self.tree(text, name))


class StyleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "table.tsv"

    def test_multiple_styles_same_node(self):
        self.path.write_text("id\ttype\tcolor\tstyle\tsize\nA\tlabel\t#0072B2\titalic\t1\nA\tbranch\t#0072B2\tdashed\t2\n")
        data = annotate(self.path, "treecolors", "Styles")
        self.assertTrue(data.startswith(b"TREE_COLORS"))
        self.assertIn(b"A\tlabel\t#0072B2\titalic\t1", data)

    def test_ranges(self):
        self.path.write_text("id\tcolor\tlabel\nA|B\t#009E73\tPlants\n")
        self.assertIn(b"A|B\trange\t#009E73\tPlants", annotate(self.path, "ranges", "Ranges"))

    def test_config_override(self):
        self.path.write_text("id\tA\nX\t2\n")
        data = annotate(self.path, "heatmap", "H", options={"COLOR_MIN": "#EEEEEE", "STRIP_WIDTH": 40})
        self.assertEqual(data.count(b"COLOR_MIN"), 1)
        self.assertIn(b"STRIP_WIDTH\t40", data)
        with self.assertRaises(ItolError):
            annotate(self.path, "heatmap", "H", options={"DATA": "inject"})
