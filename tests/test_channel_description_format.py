"""Offline public documentation contracts and shell argv checks; no API calls."""
from pathlib import Path
import json
import re
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/connect-our-agents'


def test_named_field_contract_and_examples():
    text = (SKILL / 'references/channel-description-format.md').read_text()
    for name in ('Contact label', 'Connection details', 'Contact status', 'Setup conversation', 'Invitation sender', 'Converted from mesh'):
        assert f'`{name}: `' in text
    for rule in ('mixed old/new duplicate', 'duplicate JSON keys',
                 'No bulk or read-triggered migration', 'separator newlines',
                 'unrelated description bytes', 'Tokens inside decoded JSON',
                 'Live ownership, access and outgoing shares remain authority'):
        assert rule in text
    match = re.search(r'```text\n(.*?)\n```', text, re.S)
    assert match is not None
    example = match[1]
    assert example.splitlines()[0] == 'Agent contact channel'
    for line in example.splitlines()[1:]:
        assert not line.startswith('[')
        json.loads(line.split(': ', 1)[1])


@pytest.mark.parametrize('invitation', [False, True])
@pytest.mark.parametrize('label', ["Sura Novi's agent", "Sura's \"agent\" $(exit 91) `exit 92` $HOME", 'Sura  Novi\u00a0agent'])
def test_cli_creation_preserves_json_without_shell_interpolation(label, invitation):
    text = (SKILL / 'references/cli.md').read_text()
    [example] = [block for block in re.findall(r'```bash\n(.*?)```', text, re.S)
                 if 'data-type create Event' in block]
    assert 'json.dumps' in example
    assert '-d "$description"' in example
    assert "<<'LABEL'" in example and "<<'PY'" in example
    example = example.replace("\nSura Novi's agent\n", '\n' + label + '\n')
    if invitation:
        example = example.replace('"$contact_label" <<', '"$contact_label" invitation <<')
    stub = "uvx() { python3 -c 'import json,sys; print(json.dumps(sys.argv[1:]))' \"$@\"; }\n"
    result = subprocess.run(['sh', '-c', stub + example], text=True,
                            capture_output=True, check=True)
    args = json.loads(result.stdout)
    assert args[:4] == ['fulcra-api', 'data-type', 'create', 'Event']
    description = args[args.index('-d') + 1]
    assert description.startswith('Agent contact channel')
    # Catalog folding must not change whitespace inside the decoded label.
    folded = ' '.join(description.split())
    decoder = json.JSONDecoder()
    assert decoder.raw_decode(folded.split('Contact label: ', 1)[1])[0] == label
    if invitation:
        assert 'secrets.token_hex(16)' in example
        details = decoder.raw_decode(folded.split('Connection details: ', 1)[1])[0]
        code = details['invitation']['code']
        assert re.fullmatch('[0-9a-f]{32}', code)
        assert details == {'version': 1, 'peers': [], 'invitation': {
            'code': code, 'prefix': 'handshake', 'state': 'prepared'}}
        assert description.count('Connection details: ') == 1
    else:
        assert 'Connection details: ' not in description
    assert json.loads(args[args.index('--fields') + 1]) == json.loads(
        (SKILL / 'references/channel-fields.json').read_text())


@pytest.mark.parametrize('invitation', [False, True])
def test_cli_generation_failure_does_not_create(invitation):
    text = (SKILL / 'references/cli.md').read_text()
    [example] = [block for block in re.findall(r'```bash\n(.*?)```', text, re.S)
                 if 'data-type create Event' in block]
    if invitation:
        example = example.replace('"$contact_label" <<', '"$contact_label" invitation <<')
    stub = "python3() { return 7; }; uvx() { printf 'UNEXPECTED CREATE'; };\n"
    result = subprocess.run(['sh', '-c', stub + example], text=True, capture_output=True)
    assert result.returncode == 7
    assert not result.stdout


def test_format_is_integrated_without_legacy_writes():
    main = (SKILL / 'SKILL.md').read_text()
    invite = (SKILL / 'references/invite.md').read_text()
    cli = (SKILL / 'references/cli.md').read_text()
    acceptance = (ROOT / 'tests/acceptance/connect-our-agents/connection-flow.md').read_text()
    assert 'version: "1.1.7"' in main
    assert 'optional named field' in main
    assert 'on an outbox using legacy metadata' not in main
    assert 'retain the existing named spelling or legacy wrapper' not in invite
    assert 'Preserve that wrapper' not in acceptance
    assert 'write `Connection details: ` on deliberate edits' in invite
    assert '## Metadata capabilities' in cli
    assert 'no description-update command' in cli
    assert 'no CLI equivalent' not in cli
    assert 'before step 2' in invite
    assert 'create_agent_invitation' in invite
    for path in SKILL.rglob('*.md'):
        text = path.read_text().lower()
        assert 'plugin' not in text


def test_description_reference_links_resolve():
    for path in SKILL.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if ':' not in target and not target.startswith('#'):
                assert (path.parent / target.split('#')[0]).exists(), (path, target)
