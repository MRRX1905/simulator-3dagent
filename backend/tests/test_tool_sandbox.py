import pytest
from app.tools.workspace_fs import WorkspaceFileSystem
from app.tools.command_runner import CommandRunner

def test_workspace_fs_sandboxed_operations():
    fs = WorkspaceFileSystem()
    test_file = "test_dir/sample.txt"
    content = "Hello AI City Sandbox"
    
    # Write and read within workspace
    saved = fs.write_file(test_file, content)
    assert fs.exists(test_file)
    assert fs.read_file(test_file) == content

    # Test Path Traversal Jailbreak Prevention
    with pytest.raises(PermissionError):
        fs.write_file("../../outside.txt", "Malicious content")

    with pytest.raises(PermissionError):
        fs.read_file("..\\..\\Windows\\win.ini")

def test_command_runner_allowlist():
    runner = CommandRunner()

    # Allowed command validation
    assert runner.validate_command("python --version") == "python --version"
    assert runner.validate_command("pytest") == "pytest"

    # Blocked commands
    with pytest.raises(PermissionError):
        runner.validate_command("format C:")

    with pytest.raises(PermissionError):
        runner.validate_command("shutdown /s /t 0")

    # Command outside allowlist
    with pytest.raises(PermissionError):
        runner.validate_command("curl https://unauthorized.com")

@pytest.mark.asyncio
async def test_command_runner_execution():
    runner = CommandRunner()
    result = await runner.run("python -c \"print('Hello from runner')\"")
    assert result["success"] is True
    assert "Hello from runner" in result["stdout"]
