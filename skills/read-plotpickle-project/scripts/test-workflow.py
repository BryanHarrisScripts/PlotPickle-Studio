"""Executable regression checks using synthetic story/media only."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent


class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name)
        cls.fdx = cls.base / 'synthetic.fdx'
        cls.fdx.write_text('''<FinalDraft><TitlePage><Content><Paragraph Type="Action"><Text>Not screenplay.</Text></Paragraph></Content></TitlePage><Content>
        <Paragraph Type="Scene Heading"><Text>EXT. PIER - DAWN</Text></Paragraph>
        <Paragraph Type="Action"><Text>A courier waits beside a </Text><Text Style="Bold">red door.</Text></Paragraph>
        <DualDialogue><Paragraph Type="Character"><Text>COURIER</Text></Paragraph><Paragraph Type="Dialogue"><Text>Are you there?</Text></Paragraph></DualDialogue>
        </Content><ScriptNotes><Paragraph Type="Action"><Text>Excluded annotation.</Text></Paragraph></ScriptNotes></FinalDraft>''')
        cls.original_hash = hashlib.sha256(cls.fdx.read_bytes()).hexdigest()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def invoke(self, *args, ok=True):
        r = subprocess.run(['python3', str(HERE / 'story-workflow.py'), *map(str, args)], capture_output=True, text=True)
        if ok:
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            return json.loads(r.stdout)
        self.assertNotEqual(r.returncode, 0)
        return r.stdout + r.stderr

    def pins(self, path):
        r = subprocess.run(['node', str(HERE / 'inspect-project.mjs'), '--file', str(path), '--operation', 'identity'], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        i = json.loads(r.stdout)['project']
        return ['--project', path, '--project-id', i['id'], '--revision', str(i['revision']), '--sha256', i['sha256']], i

    def imported(self, label):
        out = self.base / label
        self.invoke('import-fdx', '--file', self.fdx, '--title', 'Synthetic story', '--out', out)
        return out / 'project.ppf.json'

    def mapped(self, label):
        p = self.imported(label + '-import')
        pin, ident = self.pins(p)
        data = json.loads(p.read_text())
        mapping = {'project': ident, 'assignments': [{'passageId': x['id'], 'blockNumber': 1, 'miniBlockNumber': 1,
                    'reason': 'One opening exchange at the pier.'} for x in data['sourceEvidence']['screenplay']['passages']]}
        file = self.base / (label + '-map.json')
        file.write_text(json.dumps(mapping))
        out = self.base / (label + '-mapped')
        self.invoke('map', *pin, '--mapping', file, '--out', out)
        return out / 'project.ppf.json'

    def packet(self, p, label):
        pin, ident = self.pins(p)
        f = self.base / (label + '-plan.json')
        self.invoke('prepare-mini', *pin, '--block', '1', '--mini', '1', '--out', f)
        packet = json.loads(f.read_text())
        self.assertEqual(len(packet['shots']), 25)
        self.assertTrue(all(s['state'] == 'GAP' for s in packet['shots']))
        packet['allocationReview'] = 'Opening exchange, kept together with no new story events.'
        packet['truths'] = [{'id': 'location', 'origin': 'source', 'text': 'The setting is a pier at dawn.', 'passageIds': ['screenplay-1']}]
        packet['shots'][0] = {'shotNumber': 1, 'state': 'PLANNED', 'passageIds': ['screenplay-1', 'screenplay-2'],
            'coverageType': 'story-beat', 'narrativePurpose': 'Establish the waiting courier.',
            'composition': 'Wide view of the courier waiting beside the red door at the pier.',
            'truthIds': ['location'], 'prompt': 'One cinematic landscape frame. At dawn on the pier, a courier waits beside a red door. Wide establishing view, no text or watermark.'}
        f.write_text(json.dumps(packet))
        return f, pin, packet

    def test_fdx_source_scaffold_and_no_mutation(self):
        p = self.imported('source')
        d = json.loads(p.read_text())
        passages = d['sourceEvidence']['screenplay']['passages']
        self.assertEqual(len(passages), 4)
        self.assertEqual(passages[1]['text'], 'A courier waits beside a red door.')
        self.assertNotIn('Excluded annotation.', p.read_text())
        self.assertNotIn('Not screenplay.', p.read_text())
        self.assertEqual(len(d['structure']['blocks']), 24)
        self.assertEqual(sum(len(b['miniBlocks']) for b in d['structure']['blocks']), 96)
        self.assertEqual(d['assetRegistry']['extensions']['storyWorkflow']['allocation']['state'], 'provisional')
        self.assertEqual(hashlib.sha256(self.fdx.read_bytes()).hexdigest(), self.original_hash)

    def test_idea_needs_screenplay_then_preserves_premise(self):
        premise = self.base / 'idea.txt'
        premise.write_text('A courier waits for a message that may never arrive.')
        out = self.base / 'idea'
        self.invoke('idea', '--file', premise, '--title', 'Premise', '--out', out)
        pin, _ = self.pins(out / 'project.ppf.json')
        self.assertIn('SCREENPLAY_REQUIRED', self.invoke('prepare-mini', *pin, '--block', 1, '--mini', 1, '--out', self.base / 'bad-idea.json', ok=False))
        drafted = self.base / 'drafted'
        self.invoke('import-fdx', *pin, '--file', self.fdx, '--title', 'Premise', '--out', drafted)
        d = json.loads((drafted / 'project.ppf.json').read_text())
        self.assertEqual(d['revision'], 1)
        self.assertEqual(d['assetRegistry']['extensions']['storyWorkflow']['idea']['text'], premise.read_text())

    def test_stale_snapshot_and_existing_output_rejected(self):
        p = self.imported('stale')
        pin, _ = self.pins(p)
        pin[-1] = '0' * 64
        self.assertIn('STALE_PROJECT_SNAPSHOT', self.invoke('resume', *pin, ok=False))
        self.assertIn('OUTPUT_DIRECTORY_EXISTS', self.invoke('import-fdx', '--file', self.fdx, '--title', 'Synthetic', '--out', p.parent, ok=False))

    def test_entities_and_capacity_rejected_without_output(self):
        malicious = self.base / 'entity.fdx'
        malicious.write_text('<!DOCTYPE FinalDraft [<!ENTITY x SYSTEM "file:///etc/passwd">]><FinalDraft><Content/></FinalDraft>')
        self.assertIn('XML_ENTITIES', self.invoke('import-fdx', '--file', malicious, '--title', 'Bad', '--out', self.base / 'badxml', ok=False))
        many = self.base / 'many.fdx'
        many.write_text('<FinalDraft><Content>' + '<Paragraph Type="Action"><Text>Wait.</Text></Paragraph>' * 2501 + '</Content></FinalDraft>')
        self.assertIn('SOURCE_EXCEEDS', self.invoke('import-fdx', '--file', many, '--title', 'Too long', '--out', self.base / 'too-many', ok=False))
        self.assertFalse((self.base / 'too-many').exists())

    def test_long_paragraph_preserves_original(self):
        long = self.base / 'long.fdx'
        text = 'A long action paragraph. ' * 100
        root = ET.Element('FinalDraft'); content = ET.SubElement(root, 'Content')
        ET.SubElement(ET.SubElement(content, 'Paragraph', Type='Action'), 'Text').text = text
        long.write_bytes(ET.tostring(root))
        out = self.base / 'long'
        self.invoke('import-fdx', '--file', long, '--title', 'Long', '--out', out)
        d = json.loads((out / 'project.ppf.json').read_text())
        self.assertEqual(d['assetRegistry']['extensions']['storyWorkflow']['sourceDocument']['paragraphs'][0]['text'], text)
        self.assertGreater(len(d['sourceEvidence']['screenplay']['passages']), 1)
        self.assertTrue(all(len(p['text']) <= 780 for p in d['sourceEvidence']['screenplay']['passages']))

    def test_evidence_plan_duplicate_prompts_and_gap_integrity(self):
        p = self.mapped('plan')
        file, pin, packet = self.packet(p, 'plan')
        bad = self.base / 'bad-plan.json'
        packet['shots'][0]['passageIds'] = ['invented-passage']
        bad.write_text(json.dumps(packet))
        self.assertIn('SHOT_EVIDENCE', self.invoke('plan-mini', *pin, '--plan', bad, '--out', self.base / 'bad-plan-output', ok=False))
        packet['shots'][0]['passageIds'] = ['screenplay-2']
        second = dict(packet['shots'][0]); second['shotNumber'] = 2; packet['shots'][1] = second
        bad.write_text(json.dumps(packet))
        self.assertIn('DUPLICATE_IMAGE_PROMPT', self.invoke('plan-mini', *pin, '--plan', bad, '--out', self.base / 'duplicate-output', ok=False))
        out = self.base / 'planned'
        self.invoke('plan-mini', *pin, '--plan', file, '--out', out)
        d = json.loads((out / 'project.ppf.json').read_text())
        self.assertEqual(len(d['production']['storyboardImagePrompts']), 1)
        self.assertEqual(sum(s['state'] == 'GAP' for s in d['assetRegistry']['extensions']['storyWorkflow']['plans'][0]['shots']), 24)
        # A second process recovers the plan rather than relying on in-memory state.
        pin2, _ = self.pins(out / 'project.ppf.json')
        r = self.invoke('resume', *pin2)
        self.assertEqual(r['miniPlans'], 1)

    def test_image_candidate_recovery_replacement_and_tamper_detection(self):
        from PIL import Image
        p = self.mapped('image')
        file, pin, _ = self.packet(p, 'image')
        planned = self.base / 'image-planned'
        self.invoke('plan-mini', *pin, '--plan', file, '--out', planned)
        image = self.base / 'image.png'; Image.new('RGB', (32, 18), 'red').save(image)
        pin2, _ = self.pins(planned / 'project.ppf.json')
        out = self.base / 'with-image'
        self.invoke('attach-image', *pin2, '--block', 1, '--mini', 1, '--shot', 1, '--image', image, '--provider', 'synthetic-test', '--out', out)
        pin3, _ = self.pins(out / 'project.ppf.json')
        self.assertEqual(self.invoke('resume', *pin3)['verifiedImages'], 1)
        d = json.loads((out / 'project.ppf.json').read_text())
        self.assertEqual(d['build']['foundations']['acceptedVisualArtifactIds'], [])
        art = d['build']['foundations']['visualArtifacts'][0]
        self.assertEqual(art['reviewState'], 'draft')
        self.assertNotIn('storyboard-local-save:v1', art['sourceDecisionKeys'])
        self.assertIn('SHOT_ALREADY_HAS_IMAGE', self.invoke('attach-image', *pin3, '--block', 1, '--mini', 1, '--shot', 1, '--image', image, '--provider', 'synthetic-test', '--out', self.base / 'duplicate-image', ok=False))
        mapping = d['assetRegistry']['extensions']['storyWorkflow']['imageMappings'][0]
        (out / mapping['portablePath']).write_bytes(b'changed')
        self.assertEqual(len(self.invoke('resume', *pin3)['changedImages']), 1)
        replacement = self.base / 'replacement'
        self.invoke('attach-image', *pin3, '--block', 1, '--mini', 1, '--shot', 1, '--image', image, '--provider', 'synthetic-test', '--replace', '--out', replacement)
        replaced = json.loads((replacement / 'project.ppf.json').read_text())
        self.assertEqual(len(replaced['build']['foundations']['visualArtifacts']), 1)
        self.assertEqual(len(replaced['assetRegistry']['assets']), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
