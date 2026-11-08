// Canonical normalization adapter; imports do not execute the read-only CLI.
import { readFile, writeFile } from 'node:fs/promises';
import { parseArgs } from 'node:util';
import { normalizeLibraryProject, parseLibraryBackup } from './inspect-project.mjs';

const { values } = parseArgs({ options: {
  file: { type: 'string' }, out: { type: 'string' }, operation: { type: 'string' }
} });
try {
  if (!values.file || !values.out || !['create', 'validate'].includes(values.operation)) throw Error('INVALID_ARGUMENT');
  const bytes = await readFile(values.file);
  if (bytes.length > 20 * 1024 * 1024) throw Error('PROJECT_FILE_TOO_LARGE');
  const raw = JSON.parse(bytes.toString('utf8'));
  const project = values.operation === 'create' ? normalizeLibraryProject(raw) : parseLibraryBackup(JSON.stringify(raw));
  await writeFile(values.out, JSON.stringify(project, null, 2) + '\n', { flag: 'wx' });
  console.log(JSON.stringify({ status: 'validated', id: project.id, revision: project.revision }));
} catch (e) {
  console.error(JSON.stringify({ status: 'blocked', code: e.code === 'EEXIST' ? 'OUTPUT_EXISTS' : e.message }));
  process.exitCode = 1;
}
