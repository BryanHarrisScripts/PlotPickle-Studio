// MCP integration host. A cloud deployment must inject authenticated, owner-scoped
// project resolution and TLS; it must never rely on one global file path for all users.
// This file deliberately refuses to start until a verified authentication boundary
// is implemented. The source seam can be integrated into an existing secured host.
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { registerPlotPickleStudio } from './mcp-registration.mjs';

export function createPlotPickleStudioMcpServer(loadProjection) {
  if (typeof loadProjection !== 'function') throw Error('AUTHENTICATED_PROJECT_LOADER_REQUIRED');
  const server = new McpServer({name:'PlotPickle Studio',version:'0.2.0'});
  registerPlotPickleStudio(server,loadProjection);
  return server;
}
