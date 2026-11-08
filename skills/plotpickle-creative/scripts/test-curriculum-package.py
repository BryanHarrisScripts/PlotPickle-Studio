import importlib.util
import json
import tempfile
import tarfile
from unittest import mock
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pp_curriculum_package', HERE / 'curriculum-package.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class PackagingGates(unittest.TestCase):
    def test_incomplete_library_fails_without_output(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            with self.assertRaisesRegex(ValueError, 'Missing|source|archive'):
                module.make_overlay(base, base / 'package.tar.gz')
            self.assertFalse((base / 'package.tar.gz').exists())

    def test_canonical_inventory_counts(self):
        index = json.loads(module.INDEX.read_text(encoding='utf-8'))
        self.assertEqual(len(index['topics']), 12)
        self.assertEqual(sum(t['lessons'] for t in index['topics']), 81)
        self.assertEqual(sum(t['sources'] for t in index['topics']), 95)
        self.assertEqual(len({t['gitBlobSha1'] for t in index['topics']}),12)

    def test_full_synthetic_package_roundtrip(self):
        # Synthetic fixture exercises all checks without presenting invented lessons as genuine.
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); src=base/'source';src.mkdir()
            original=json.loads(module.INDEX.read_text())
            number=0
            for t in original['topics']:
                lessons=[]
                for k in range(t['lessons']):
                    number+=1
                    lesson_sources=[]
                    if k==0:
                        lesson_sources=[{'id':f'{t["id"]}-source-{j}', 'content':'Synthetic teaching'} for j in range(t['sources'])]
                    lessons.append({'id':f'fixture-{k}', 'topic':t['id'], 'number':number,
                                    'title':f'Fixture Lesson {number}', 'sources':lesson_sources})
                raw=(json.dumps({'schemaVersion':'2.0','topic':{'id':t['id']},
                                 'lessonCount':t['lessons'],'sourceCount':t['sources'],
                                 'lessons':lessons},ensure_ascii=False)+'\n').encode()
                (src/t['file']).write_bytes(raw)
                t['gitBlobSha1']=module.load_bridge().git_blob_id(raw)
            fakeindex=base/'index.json'
            fakeindex.write_text(json.dumps(original))
            output=base/'package.tar.gz'
            with mock.patch.object(module,'INDEX',fakeindex):
                meta=module.make_overlay(src,output)
            self.assertEqual(12,meta['topicCount'])
            self.assertEqual(81,meta['lessonCount'])
            self.assertEqual(95,meta['sourceCount'])
            with tarfile.open(output,'r:gz') as archive:
                files=archive.getnames()
                self.assertEqual(13,len(files))
                for t in original['topics']:
                    member='skills/plotpickle-creative/data/learn/'+t['file']
                    self.assertEqual((src/t['file']).read_bytes(),archive.extractfile(member).read())

    def test_invalid_hash_prevents_archive(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src = base / 'learn'; src.mkdir()
            for x in json.loads(module.INDEX.read_text())['topics']:
                (src / x['file']).write_text('{}')
            with self.assertRaisesRegex(ValueError,'identity mismatch'):
                module.make_overlay(src, base/'package.tar.gz')
            self.assertFalse((base / 'package.tar.gz').exists())

if __name__ == '__main__': unittest.main()
