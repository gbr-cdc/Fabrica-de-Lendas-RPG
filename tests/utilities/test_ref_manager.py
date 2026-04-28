import pytest
import os
import shutil
import re
from utilities import ref_manager

TEST_FILE = "tests/test_run.md"
ORIGINAL_TEST_FILE = "tests/test.md"

@pytest.fixture(autouse=True)
def setup_test_file():
    # Copy the test.md to a temporary file for testing
    shutil.copy(ORIGINAL_TEST_FILE, TEST_FILE)
    # Patch PATH_MAPPING to use the temporary file
    original_mapping = ref_manager.PATH_MAPPING.copy()
    ref_manager.PATH_MAPPING["TESTE."] = TEST_FILE
    yield
    # Restore mapping and cleanup
    ref_manager.PATH_MAPPING = original_mapping
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

def test_get_path_for_tag():
    assert ref_manager.get_path_for_tag("[TESTE.BASIC]") == TEST_FILE
    assert ref_manager.get_path_for_tag("ARCH.DOC") == ".forbidden/architecture.md"
    assert ref_manager.get_path_for_tag("[INVALID.TAG]") is None

def test_find_tag_range_basic():
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    start, end, is_header = ref_manager.find_tag_range("[TESTE.BASIC]", lines)
    assert start is not None
    assert is_header is True
    assert "## Basic Section [TESTE.BASIC]" in lines[start]
    assert "This is a basic section content." in lines[start+1]

def test_find_tag_range_unicode():
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    start, end, is_header = ref_manager.find_tag_range("[TESTE.AÇÃO]", lines)
    assert start is not None
    assert "[TESTE.AÇÃO]" in lines[start]

def test_extract_section():
    content = ref_manager.extract_section("[TESTE.BASIC]", TEST_FILE)
    assert "## Basic Section [TESTE.BASIC]" in content
    assert "This is a basic section content." in content

def test_extract_section_nested():
    content = ref_manager.extract_section("[TESTE.PARENT]", TEST_FILE)
    # Parent should include Child because it's a subheader (level 2 vs level 3)
    assert "## Parent Section [TESTE.PARENT]" in content
    assert "### Child Section [TESTE.CHILD]" in content

def test_extract_section_child_only():
    content = ref_manager.extract_section("[TESTE.CHILD]", TEST_FILE)
    assert "### Child Section [TESTE.CHILD]" in content
    assert "Child content." in content
    assert "## Parent Section" not in content

def test_update_section():
    new_content = "## Updated Section [TESTE.BASIC]\nNew content here."
    success, msg = ref_manager.update_section("[TESTE.BASIC]", new_content, TEST_FILE)
    assert success is True
    
    updated_content = ref_manager.extract_section("[TESTE.BASIC]", TEST_FILE)
    assert "New content here." in updated_content
    assert "This is a basic section content." not in updated_content

def test_create_section_after():
    content = "## Created After [TESTE.AFTER]\nContent."
    success, msg = ref_manager.create_section(content, TEST_FILE, after_tag="[TESTE.BASIC]")
    assert success is True
    
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    assert "## Basic Section [TESTE.BASIC]\nThis is a basic section content.\n\n## Created After [TESTE.AFTER]" in text

def test_smart_placement():
    # Create [TESTE.SMART_NEW] which should be placed after [TESTE.SMART_2]
    tag = "[TESTE.SMART_NEW]"
    content = "## New Smart Section [TESTE.SMART_NEW]\nSmart content."
    success, msg = ref_manager.create_section(content, TEST_FILE, target_tag=tag)
    
    assert success is True
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # It should be after SMART_2 because they share the pattern "TESTE.SMART."
    assert "## Smart Placement Test [TESTE.SMART_2]\nContent 2.\n\n## New Smart Section [TESTE.SMART_NEW]" in text

def test_resolve_tag_circular():
    # TESTE.DEP_A depends on TESTE.DEP_B which depends on TESTE.DEP_A
    result = ref_manager.resolve_tag("[TESTE.DEP_A]")
    # Circularity check: should not hang and should contain content from both
    assert "## Dependency Section [TESTE.DEP_B]" in result
    assert "## Dependency Section [TESTE.DEP_A]" in result
    # The error logic in ref_manager for circularity is just returning "" if already resolved
    # So DEP_A (top) -> DEP_B (dep) -> DEP_A (skipped)
    # Result: Content B + Content A
    assert "Content B." in result
    assert "Content A." in result

def test_resolve_tag_multi():
    result = ref_manager.resolve_tag("[TESTE.MULTI]")
    assert "## Basic Section [TESTE.BASIC]" in result
    assert "## Header Section [TESTE.HEADER]" in result
    assert "## Multi Dependency [TESTE.MULTI]" in result

def test_resolve_tag_session():
    # [TESTE.SESSION_PARENT] contains [TESTE.INNER_1] and [TESTE.INNER_2]
    resolved = set()
    ref_manager.resolve_tag("[TESTE.SESSION_PARENT]", resolved_tags=resolved)
    
    assert f"{TEST_FILE}:TESTE.INNER_1" in resolved
    assert f"{TEST_FILE}:TESTE.INNER_2" in resolved

def test_resolve_tag_missing():
    result = ref_manager.resolve_tag("[TESTE.NON_EXISTENT]")
    assert "Error: Tag [TESTE.NON_EXISTENT] not found" in result

def test_get_path_for_tag_unmapped():
    assert ref_manager.get_path_for_tag("[UNKNOWN.TAG]") is None
    result = ref_manager.resolve_tag("[UNKNOWN.TAG]")
    assert "Error: No path mapping found" in result

def test_delete_section_middle():
    # Delete [TESTE.HEADER], which is in the middle
    success, msg = ref_manager.delete_section("[TESTE.HEADER]", TEST_FILE)
    assert success is True
    
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Should leave only one blank line between BASIC and PARENT
    assert "## Basic Section [TESTE.BASIC]\nThis is a basic section content.\n\n## Parent Section [TESTE.PARENT]" in text
    assert "[TESTE.HEADER]" not in text

def test_delete_section_first():
    # Setup: add a section at the very beginning of the file
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    lines.insert(0, "## First Section [TESTE.FIRST]\n")
    lines.insert(1, "First content.\n")
    lines.insert(2, "\n")
    with open(TEST_FILE, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    # Delete the newly added first section
    success, msg = ref_manager.delete_section("[TESTE.FIRST]", TEST_FILE)
    assert success is True
    
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Should not have leading blank lines and should start with the original first section
    assert text.startswith("# Test File [TESTE.ROOT]")
    assert "[TESTE.FIRST]" not in text

def test_delete_section_last():
    # Delete [TESTE.SMART_2], which is the last section
    success, msg = ref_manager.delete_section("[TESTE.SMART_2]", TEST_FILE)
    assert success is True
    
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Should not have trailing blank lines (except standard EOF newline if present)
    assert text.endswith("Content 1.") or text.endswith("Content 1.\n")
    assert "[TESTE.SMART_2]" not in text

def test_delete_section_non_existent():
    success, msg = ref_manager.delete_section("[TESTE.NON_EXISTENT]", TEST_FILE)
    assert success is False
    assert "Error: Tag [[TESTE.NON_EXISTENT]] not found" in msg

def test_extract_section_code_block():
    content = ref_manager.extract_section("[TESTE.CODE_BLOCK]", TEST_FILE)
    assert "## Code Block Test [TESTE.CODE_BLOCK]" in content
    assert "## This should not be a header [TESTE.INSIDE_CODE]" in content
    assert "Final line of section." in content
    assert "```markdown" in content

def test_resolve_tag_code_block_session():
    resolved = set()
    ref_manager.resolve_tag("[TESTE.CODE_BLOCK]", resolved_tags=resolved)
    
    # TESTE.CODE_BLOCK should be resolved
    assert f"{TEST_FILE}:TESTE.CODE_BLOCK" in resolved
    # TESTE.INSIDE_CODE should NOT be resolved because it's in a code block
    assert f"{TEST_FILE}:TESTE.INSIDE_CODE" not in resolved

def test_create_section_duplicate():
    tag = "[TESTE.BASIC]"
    content = "## Duplicate [TESTE.BASIC]\nContent."
    success, msg = ref_manager.create_section(content, TEST_FILE, target_tag=tag)
    assert success is False
    assert "Error: Tag [TESTE.BASIC] already exists" in msg

def test_create_section_fail_fast_parent_missing():
    # TESTE.NON_EXISTENT.CHILD should fail because TESTE.NON_EXISTENT is missing
    tag = "[TESTE.NON_EXISTENT.CHILD]"
    content = "### Child [TESTE.NON_EXISTENT.CHILD]\nContent."
    success, msg = ref_manager.create_section(content, TEST_FILE, target_tag=tag)
    assert success is False
    assert "Error: Parent tag [TESTE.NON_EXISTENT] not found" in msg

def test_create_section_fail_fast_identifier_missing():
    tag = "[INVALID.NEW]"
    # Ensure PATH_MAPPING has INVALID.
    original_mapping = ref_manager.PATH_MAPPING.copy()
    ref_manager.PATH_MAPPING["INVALID."] = TEST_FILE # Pointing to TEST_FILE which has no INVALID tags
    try:
        content = "## Invalid [INVALID.NEW]\nContent."
        success, msg = ref_manager.create_section(content, TEST_FILE, target_tag=tag)
        assert success is False
        assert "Error: File identifier [INVALID] not found" in msg
    finally:
        ref_manager.PATH_MAPPING = original_mapping

def test_smart_placement_new_hierarchy():
    # [TESTE.PARENT.NEW_CHILD] should be placed after [TESTE.CHILD] (which is a child of PARENT)
    tag = "[TESTE.PARENT.NEW_CHILD]"
    content = "### New Child [TESTE.PARENT.NEW_CHILD]\nNew child content."
    success, msg = ref_manager.create_section(content, TEST_FILE, target_tag=tag)
    assert success is True
    
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # In test.md, [TESTE.CHILD] is the only child of [TESTE.PARENT]
    # It ends with a horizontal rule '---' and some blank lines.
    assert "### Child Section [TESTE.CHILD]\nChild content.\n\n---\n\n### New Child [TESTE.PARENT.NEW_CHILD]" in text
