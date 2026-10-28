"""Small static checks of the documented public description wire contract."""
from pathlib import Path
import re
import json
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/connect-our-agents'


def test_named_field_contract_and_examples():
    text = (SKILL / 'references/channel-description-format.md').read_text()
    for name in ('Contact label', 'Connection details', 'Contact status', 'Setup conversation', 'Invitation sender', 'Converted from mesh'):
        assert f'`{name}: `' in text
    assert 'mixed old/new duplicate' in text
    assert 'No bulk or read-triggered migration' in text
    assert 'Live ownership, access and outgoing shares remain authority' in text
    example = re.search(r'```text\n(.*?)\n```', text, re.S)[1]
    assert example.splitlines()[0] == 'Agent contact channel'
    for line in example.splitlines()[1:]:
        assert not line.startswith('[')
        json.loads(line.split(': ', 1)[1])


@pytest.mark.parametrize('label', ["Sura Novi's agent", "Sura's \"agent\" $(exit 91) `exit 92` $HOME"])
def test_cli_creation_preserves_json_without_shell_interpolation(label):
    text = (SKILL / 'references/cli.md').read_text()
    assert '[channel description format](channel-description-format.md)' in text
    [example] = [block for block in re.findall(r'```bash\n(.*?)```', text, re.S)
                 if 'data-type create Event' in block]
    assert 'json.dumps' in example
    assert '-d "$description"' in example
    assert "<<'LABEL'" in example and "<<'PY'" in example
    example = example.replace("\nSura Novi's agent\n", '\n' + label + '\n')
    # Only the shell/JSON example runs; the API command is an offline argv capture.
    stub = "uvx() { python3 -c 'import json,sys; print(json.dumps(sys.argv[1:]))' \"$@\"; }\n"
    result = subprocess.run(['sh', '-c', stub + example], text=True,
                            capture_output=True, check=True)
    args = json.loads(result.stdout)
    assert args[:4] == ['fulcra-api', 'data-type', 'create', 'Event']
    description = args[args.index('-d') + 1]
    assert description.startswith('Agent contact channel')
    assert json.loads(description.split('Contact label: ', 1)[1]) == label
    assert json.loads(args[args.index('--fields') + 1]) == json.loads(
        (SKILL / 'references/channel-fields.json').read_text())


def test_cli_metadata_capability_gate_precedes_creation():
    skill = (SKILL / 'SKILL.md').read_text()
    cli = (SKILL / 'references/cli.md').read_text()
    invite = (SKILL / 'references/invite.md').read_text()
    wire = (SKILL / 'references/channel-description-format.md').read_text()
    assert 'Either does everything here' not in skill
    assert skill.index('## Operation prerequisites') < skill.index('## Channel matching')
    assert 'no description-update command' in cli
    assert 'Ordinary CLI connections and sends remain supported' in cli
    assert invite.index('Before creating a channel') < invite.index('- Create your channel')
    assert 'CLI-only' in invite and 'state transitions' in invite
    assert '## MCP-specific readback and consent' in wire
    assert 'Deploy the server support before publishing new metadata consumers' in wire


def test_description_reference_links_resolve():
    for path in SKILL.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if ':' not in target and not target.startswith('#'):
                assert (path.parent / target.split('#')[0]).exists(), (path, target)
