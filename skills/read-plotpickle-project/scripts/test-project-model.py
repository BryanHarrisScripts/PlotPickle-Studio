"""Executable checks for provenance, explicit adoption, runtime math and recovery."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        fdx = self.base / 'input.fdx'
        fdx.write_text('<FinalDraft><Content><Paragraph Type="Scene Heading"><Text>EXT. PIER - DAWN</Text></Paragraph><Paragraph Type="Action"><Text>A courier waits beside a red door.</Text></Paragraph><Paragraph Type="Dialogue"><Text>Are you there?</Text></Paragraph></Content></FinalDraft>')
        self.command('story-workflow.py', 'import-fdx', '--file', fdx, '--title', 'Synthetic fixture', '--out', self.base / 'initial')
        self.project = self.base / 'initial/project.ppf.json'

    def tearDown(self):
        self.tmp.cleanup()

    def command(self, script, *args, ok=True):
        result = subprocess.run(['python3', str(HERE / script), *map(str, args)], capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        return result.stdout + result.stderr

    def ident(self, project):
        result = subprocess.run(['node', str(HERE / 'inspect-project.mjs'), '--file', str(project), '--operation', 'identity'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        return json.loads(result.stdout)['project']

    def pins(self, project):
        i = self.ident(project)
        return ['--project', project, '--project-id', i['id'], '--revision', i['revision'], '--sha256', i['sha256']]

    def write(self, name, payload):
        path = self.base / name
        path.write_text(json.dumps(payload))
        return path

    def payload(self):
        source = json.loads(self.project.read_text())['sourceEvidence']['screenplay']['passages']
        a = source[1]
        return {'project': self.ident(self.project),
            'truths': [
                {'id': 'location', 'category': 'known', 'scope': 'source-observation', 'origin': 'supplied-source', 'text': 'The scene heading says pier at dawn.', 'passageIds': ['screenplay-1'], 'reason': 'Direct heading observation.'},
                {'id': 'hesitation', 'category': 'proposed', 'scope': 'story-world', 'origin': 'synthetic', 'text': 'The courier hesitates before knocking.', 'passageIds': [], 'reason': 'A proposed uncertainty beat.'},
                {'id': 'recipient', 'category': 'unknown', 'scope': 'story-world', 'origin': 'unresolved', 'text': 'The recipient is unspecified.', 'passageIds': [], 'reason': 'No identity is supplied.'}],
            'storySummary': {part: {'text': 'A courier waits and asks a question.', 'passageIds': ['screenplay-2', 'screenplay-3']} for part in ['beginning', 'middle', 'ending']},
            'findings': [{'id': 'pace', 'classification': 'opportunity', 'claim': 'An optional pause may develop anticipation.', 'reason': 'Editorial option, not proof that a gap exists.', 'passageIds': ['screenplay-2']}],
            'proposals': [{'id': 'pause', 'title': 'A moment before knocking', 'diagnosis': 'The exchange moves quickly.', 'rationale': 'A pause could build anticipation.', 'findingId': 'pace', 'passageIds': ['screenplay-2'], 'truthIds': ['hesitation'], 'recommendation': 'insert',
                'change': {'afterPassageId': 'screenplay-2', 'blockNumber': a['blockNumber'], 'miniBlockNumber': a['miniBlockNumber'], 'passages': [{'type': 'action', 'text': 'The courier raises a hand, hesitates, then knocks.'}]},
                'learning': {'principle': 'Anticipation', 'explanation': 'A visible decision can create a question.', 'studentQuestion': 'Does the pause strengthen or slow the scene?'},
                'impacts': [{'area': 'shot-plan', 'reason': 'The additional action may need another view or a longer hold.'}]}]}

    def assess(self):
        file = self.write('assessment.json', self.payload())
        self.command('project-model.py', 'assess', *self.pins(self.project), '--file', file, '--out', self.base / 'assessed')
        return self.base / 'assessed/project.ppf.json'

    def test_assessment_is_proposal_and_does_not_rewrite_source(self):
        path = self.assess()
        old = json.loads(self.project.read_text());new = json.loads(path.read_text())
        self.assertEqual(new['sourceEvidence'], old['sourceEvidence'])
        self.assertEqual(new['build'], old['build'])
        observed = self.command('project-model.py', 'inspect', *self.pins(path))
        self.assertEqual(observed['projectModel']['proposals'][0]['status'], 'proposed')
        self.assertFalse(observed['semanticTruthIndependentlyVerified'])

    def test_adoption_retains_origin_and_all_original_passages(self):
        path = self.assess();ident = self.ident(path)
        file = self.write('decision.json', {'project': ident, 'authority': 'Synthetic test adoption', 'reason': 'Exercise the explicit transition.'})
        self.command('project-model.py', 'adopt-proposal', *self.pins(path), '--proposal', 'pause', '--file', file, '--out', self.base / 'adopted')
        p = json.loads((self.base / 'adopted/project.ppf.json').read_text())
        originals = json.loads(self.project.read_text())['sourceEvidence']['screenplay']['passages']
        self.assertEqual([x for x in p['sourceEvidence']['screenplay']['passages'] if not x['id'].startswith('synthetic-')], originals)
        m = p['assetRegistry']['extensions']['projectModel']
        truth = next(t for t in m['truths'] if t['id'] == 'hesitation')
        self.assertEqual((truth['category'], truth['originalCategory'], truth['origin']), ('adopted', 'proposed', 'synthetic'))
        self.assertTrue(m['reviewRequired'])
        self.assertEqual(len(p['sourceEvidence']['screenplay']['passages']), 4)

    def test_invalid_truth_certainty_and_unresolved_references_block(self):
        payload = self.payload();payload['truths'][0]['scope'] = 'story-world'
        file = self.write('bad.json', payload)
        self.assertIn('WORLD_FACT_REQUIRES_REVIEW', self.command('project-model.py', 'assess', *self.pins(self.project), '--file', file, '--out', self.base / 'bad', ok=False))
        payload = self.payload();payload['truths'][0]['passageIds'] = ['missing']
        file.write_text(json.dumps(payload))
        self.assertIn('SOURCE_REFERENCE_UNRESOLVED', self.command('project-model.py', 'assess', *self.pins(self.project), '--file', file, '--out', self.base / 'bad', ok=False))

    def test_declared_contradictions_remain_visible(self):
        payload = self.payload();payload['truths'].append({'id': 'other-reading', 'category': 'inferred', 'scope': 'editorial-judgment', 'origin': 'interpretation', 'text': 'An alternative reading questions the setting.', 'passageIds': ['screenplay-1'], 'reason': 'Synthetic contradiction test.', 'relations': [{'kind': 'contradicts', 'truthId': 'location', 'reason': 'Conflicting readings must remain inspectable.'}]})
        file = self.write('contradiction.json', payload)
        self.command('project-model.py', 'assess', *self.pins(self.project), '--file', file, '--out', self.base / 'contradiction')
        result = self.command('project-model.py', 'inspect', *self.pins(self.base / 'contradiction/project.ppf.json'))
        self.assertEqual(len(result['declaredContradictions']), 1)
        self.assertFalse(result['contradictionsAutomaticallyDetected'])

    def test_runtime_compression_exact_frames_and_no_fake_completeness(self):
        def address(shot):
            return dict(actNumber=1, sequenceNumber=1, blockNumber=1, miniBlockNumber=1, shotNumber=shot)
        payload = {'project': self.ident(self.project), 'intendedFormat': 'short', 'targetRuntimeSeconds': 600, 'targetBasis': 'Hypothetical ten-minute test target, not an inferred source duration.', 'framesPerSecond': 24,
            'physicalShots': [{'id': 'p1', 'durationSeconds': 2.5, 'slotRefs': [address(1), address(2)], 'coverageReason': 'One physical view can represent two planning positions.'}, {'id': 'p2', 'durationSeconds': 3, 'slotRefs': [address(3)], 'coverageReason': 'A second view.'}]}
        file = self.write('runtime.json', payload)
        self.command('project-model.py', 'runtime-plan', *self.pins(self.project), '--file', file, '--out', self.base / 'runtime')
        p = json.loads((self.base / 'runtime/project.ppf.json').read_text());r = p['assetRegistry']['extensions']['projectModel']['runtimePlan']['computed']
        self.assertEqual((r['physicalShotCount'], r['coveredCanonicalSlots'], r['plannedRuntimeSeconds'], r['nearestFrameCount']), (2, 3, 5.5, 132))
        self.assertFalse(r['structuralCoverageProved']);self.assertFalse(r['actualMediaRuntimeVerified'])
        payload['physicalShots'][1]['slotRefs'] = [address(2)];file.write_text(json.dumps(payload))
        self.assertIn('SLOT_ASSIGNED_TO_MULTIPLE', self.command('project-model.py', 'runtime-plan', *self.pins(self.project), '--file', file, '--out', self.base / 'bad-runtime', ok=False))

    def test_feedback_records_learning_without_claiming_model_training(self):
        path = self.assess()
        payload = {'project': self.ident(path), 'proposalId': 'pause', 'reportedBy': 'user', 'observation': 'The pause feels too long.', 'evidence': 'Synthetic test review note.', 'lesson': 'Anticipation must suit pacing.', 'nextExperiment': 'Try a shorter pause.'}
        file = self.write('feedback.json', payload)
        self.command('project-model.py', 'record-feedback', *self.pins(path), '--file', file, '--out', self.base / 'feedback')
        result = self.command('project-model.py', 'inspect', *self.pins(self.base / 'feedback/project.ppf.json'))
        self.assertFalse(result['projectModel']['feedback'][0]['modelWeightsUpdated'])

    def test_assessment_scope_excludes_unrelated_passages(self):
        payload = self.payload()
        payload['scopePassageIds'] = ['screenplay-1', 'screenplay-2']
        for part in payload['storySummary'].values():
            part['passageIds'] = ['screenplay-2']
        payload['truths'][0]['passageIds'] = ['screenplay-3']
        file = self.write('out-of-scope.json', payload)
        self.assertIn('SOURCE_REFERENCE_UNRESOLVED', self.command('project-model.py', 'assess', *self.pins(self.project), '--file', file, '--out', self.base / 'out-of-scope', ok=False))

    def test_source_change_blocks_stale_adoption(self):
        path = self.assess()
        changed = json.loads(path.read_text())
        changed['sourceEvidence']['screenplay']['passages'][1]['text'] = 'A courier has left the pier.'
        changed['revision'] += 1
        edited = self.base / 'edited.ppf.json'
        edited.write_text(json.dumps(changed))
        file = self.write('stale-adoption.json', {'project': self.ident(edited), 'authority': 'Synthetic test instruction', 'reason': 'Try a stale proposal against changed source.'})
        self.assertIn('SOURCE_CHANGED_REASSESS_PROPOSAL', self.command('project-model.py', 'adopt-proposal', *self.pins(edited), '--proposal', 'pause', '--file', file, '--out', self.base / 'stale-adoption', ok=False))


if __name__ == '__main__':
    unittest.main(verbosity=2)
