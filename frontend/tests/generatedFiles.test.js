import assert from 'node:assert/strict';
import test from 'node:test';

import { reconcileSelectedFile } from '../src/utils/generatedFiles.js';

test('refreshes the selected file object when regenerated content changes', () => {
  const selectedFile = { path: 'index.html', content: '<p>old</p>' };
  const refreshedFiles = [
    { path: 'index.html', content: '<p>new speed level</p>' },
  ];

  assert.equal(
    reconcileSelectedFile(refreshedFiles, selectedFile),
    refreshedFiles[0],
  );
});

test('falls back to the first file when the previous path no longer exists', () => {
  const refreshedFiles = [{ path: 'main.js', content: 'startGame();' }];

  assert.equal(
    reconcileSelectedFile(
      refreshedFiles,
      { path: 'index.html', content: '<p>removed</p>' },
    ),
    refreshedFiles[0],
  );
});

test('returns null when a project has no generated files', () => {
  assert.equal(
    reconcileSelectedFile([], { path: 'index.html', content: '<p>old</p>' }),
    null,
  );
});
