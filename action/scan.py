"""
constituicao.tech GitHub Action — Document Scanner

Scans changed files in a PR for prompt injection vectors,
academic integrity issues, and signature anomalies.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'detector-py'))

from detector.core import analisar
from detector.integridade import analisar_integridade
from detector.extracao import extrair


def get_changed_files():
    """Get files changed in the PR via git diff."""
    import subprocess
    result = subprocess.run(
        ['git', 'diff', '--name-only', '--diff-filter=ACMR', 'HEAD~1'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        result = subprocess.run(
            ['git', 'diff', '--name-only', '--diff-filter=ACMR', 'origin/main...HEAD'],
            capture_output=True, text=True
        )
    return result.stdout.strip().split('\n') if result.stdout.strip() else []


def match_patterns(files, patterns):
    """Filter files by glob patterns."""
    pattern_list = [p.strip() for p in patterns.split(',')]
    matched = set()
    for pattern in pattern_list:
        for f in files:
            import fnmatch
            if fnmatch.fnmatch(f, pattern):
                matched.add(f)
    return list(matched)


def scan_file(filepath, mode):
    """Scan a single file and return results."""
    try:
        if filepath.endswith('.pdf') or filepath.endswith('.docx'):
            with open(filepath, 'rb') as f:
                texto = extrair(f.read(), filepath.split('.')[-1])
        else:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                texto = f.read()

        if not texto or len(texto.strip()) < 10:
            return None

        results = {}

        if mode in ('injection', 'all'):
            r = analisar(texto)
            results['injection'] = {
                'score': r.score_risco,
                'nivel': r.nivel,
                'achados': len(r.achados),
            }

        if mode in ('integridade', 'all'):
            r = analisar_integridade(texto)
            results['integridade'] = {
                'score': r.score_ia,
                'classificacao': r.classificacao,
            }

        return results
    except Exception as e:
        print(f"  Warning: could not scan {filepath}: {e}")
        return None


def set_output(name, value):
    """Set GitHub Actions output."""
    output_file = os.environ.get('GITHUB_OUTPUT', '')
    if output_file:
        with open(output_file, 'a') as f:
            f.write(f"{name}={value}\n")


def main():
    mode = os.environ.get('SCAN_MODE', 'injection')
    threshold = int(os.environ.get('THRESHOLD', '30'))
    patterns = os.environ.get('FILE_PATTERNS', '**/*.pdf,**/*.docx,**/*.txt,**/*.md')
    fail_on_detection = os.environ.get('FAIL_ON_DETECTION', 'true').lower() == 'true'

    changed_files = get_changed_files()
    if not changed_files:
        print("No changed files found.")
        set_output('files-scanned', '0')
        set_output('score', '0')
        set_output('level', 'baixo')
        set_output('detections', '0')
        return

    files_to_scan = match_patterns(changed_files, patterns)
    print(f"Scanning {len(files_to_scan)} files (mode: {mode}, threshold: {threshold})")

    max_score = 0.0
    detections = 0
    scanned = 0

    for filepath in files_to_scan:
        if not os.path.exists(filepath):
            continue
        print(f"  Scanning: {filepath}")
        result = scan_file(filepath, mode)
        if result is None:
            continue
        scanned += 1

        for module, data in result.items():
            score = data.get('score', 0)
            if score > max_score:
                max_score = score
            if score >= threshold:
                detections += 1
                print(f"    [{module}] score={score} (above threshold {threshold})")

    level = 'baixo' if max_score < 12 else ('atencao' if max_score < 30 else 'elevado')

    print(f"\nResults: {scanned} scanned, {detections} detections, max score={max_score}, level={level}")

    set_output('files-scanned', str(scanned))
    set_output('score', str(max_score))
    set_output('level', level)
    set_output('detections', str(detections))

    if fail_on_detection and detections > 0:
        print(f"\nFailing: {detections} file(s) above threshold {threshold}")
        sys.exit(1)


if __name__ == '__main__':
    main()
