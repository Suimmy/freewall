/**
 * In-browser ONNX Runtime Web wrapper for AI text / image detectors.
 *
 * TODO (Phase 4): wire onnxruntime-web (~3 MB bundle, deferred until E exports models)
 *                  per CLAUDE.md decision #10 — MoA-style ensemble of multiple HF detectors.
 * Models will live in extension/public/models/ and load via chrome.runtime.getURL.
 *
 * Today returns 0.5 placeholder — neutral so UI doesn't surface false positives during scaffold.
 */

export async function detectAiText(_text: string): Promise<{ score: number }> {
  return { score: 0.5 }
}

export async function detectAiImage(_imageUrl: string): Promise<{ score: number }> {
  return { score: 0.5 }
}
