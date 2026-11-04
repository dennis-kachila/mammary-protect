"""Run KiCad checks and refresh the review artifacts for all three sheets."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CLI = shutil.which('kicad-cli') or r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'


def run(*args: str):
    subprocess.run(args, cwd=ROOT, check=True)


for name in ('temperature-node', 'temperature-hub', 'probe-interface'):
    source = f'{name}.kicad_sch'
    run(CLI, 'sch', 'erc', source, '-o', f'{name}-erc.txt')
    report = (ROOT / f'{name}-erc.txt').read_text(encoding='utf-8')
    result = re.search(r'ERC messages:\s*(\d+)\s+Errors\s+(\d+)\s+Warnings', report)
    if not result or result.group(1) != '0' or result.group(2) != '0':
        raise RuntimeError(f'{name} ERC is not clean: {result.group(0) if result else "no summary"}')
    run(CLI, 'sch', 'export', 'pdf', source, '-o', f'{name}.pdf')
    run(CLI, 'sch', 'export', 'netlist', source, '-o', f'{name}.net')
    run(CLI, 'sch', 'export', 'bom', source, '-o', f'{name}-bom.csv')
    if shutil.which('pdftoppm'):
        size = '1800' if name == 'temperature-hub' else '1200'
        run('pdftoppm', '-f', '1', '-singlefile', '-scale-to', size,
            '-png', f'{name}.pdf', f'{name}-preview')
    print(f'{name}: ERC clean, exports refreshed', flush=True)
