// PlotPickle Studio source adapter. Do not serve arbitrary private PPFs from remote paths.
// The owning authenticated host supplies one explicitly scoped project and native reader.
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { projectStudio } from './projection.mjs';

const execFileAsync = promisify(execFile);

export function createProjectLoader({ projectFile, inspector, execute = execFileAsync, read = readFile }={}) {
  return async function loadProjection() {
    if (!projectFile || !inspector) return {
      status: 'unconnected', readonly: true,
      message: 'No saved project has been opened through the authorized PlotPickle reader.'
    };
    try {
      const file = resolve(projectFile);
      const reader = resolve(inspector);
      // This reads the whole source exactly once and passes the ORIGINAL bytes to SHA-256 validation.
      const bytes = await read(file);
      if (bytes.length > 40 * 1024 * 1024) throw Error('PROJECT_TOO_LARGE');
      const ppf = JSON.parse(bytes.toString('utf8'));
      const {stdout} = await execute(process.execPath,[reader,'--file',file,'--operation','identity'],
        {timeout:15000,maxBuffer:3e6});
      const parsed = JSON.parse(stdout);
      const identity = parsed?.project;
      // The native reader authenticates identity, revision and hash of the exact file path.
      const data = projectStudio(ppf, bytes, identity);
      return {status:'source-backed',readonly:true,data};
    } catch (err) {
      const message = String(err?.message||'unknown');
      return {status:'blocked',readonly:true,
        // Never send a private path, raw source, provider secret, or stack trace to an app view.
        reason: /SOURCE_FINGERPRINT_MISMATCH|IDENTITY_REVISION_MISMATCH|NATIVE_IDENTITY_REQUIRED|PROJECT_TOO_LARGE|INVALID_PROJECT|CONFLICTING_/.test(message)
          ? message.match(/^[A-Z_]+/)?.[0] || 'PROJECT_VERIFICATION_FAILED'
          : 'NATIVE_PROJECT_READER_UNAVAILABLE',
        message:'Unable to verify the saved project. No source details were shown or changed.'};
    }
  };
}
