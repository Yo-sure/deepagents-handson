import { loadPyodide } from 'https://cdn.jsdelivr.net/pyodide/v314.0.6/full/pyodide.mjs';
let runtime;
self.onmessage = async ({ data }) => {
  try {
    runtime ??= await loadPyodide();
    if (data.packages?.includes('pydantic')) await runtime.loadPackage('pydantic');
    self.postMessage({ type: 'ready' });
    let output = '';
    const capture = text => { output = (output + text + '\n').slice(-16000); };
    runtime.setStdout({ batched: capture });
    runtime.setStderr({ batched: capture });
    const globals = runtime.toPy({});
    try {
      const value = await runtime.runPythonAsync(data.code, { globals });
      value?.destroy?.();
      self.postMessage({ type: 'done', output: output || '(출력 없음: print()로 결과를 표시합니다.)' });
    } finally { globals.destroy(); }
  } catch (error) { self.postMessage({ type: 'error', output: String(error) }); }
};
