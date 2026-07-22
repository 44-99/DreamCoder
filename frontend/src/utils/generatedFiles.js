export function reconcileSelectedFile(files, selectedFile) {
  if (files.length === 0) return null;

  if (!selectedFile) return files[0];

  return files.find(file => file.path === selectedFile.path) ?? files[0];
}
