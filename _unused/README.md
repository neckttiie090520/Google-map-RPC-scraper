# Unused Files Archive

This folder contains files that are not actively used by the main applications but are kept for reference and potential future use.

## Folder Structure

### `/debug/`
Debug scripts and tools that were used during development:
- `debug_actual_place_data.py` - Debug place data extraction
- `debug_coordinates.py` - Coordinate handling debugging
- `debug_current_response.py` - Response parsing debug
- `debug_direct_details.py` - Direct details debugging
- `debug_direct_response.html` - Direct response HTML
- `debug_direct_result.py` - Direct result debugging
- `debug_direct_structure.py` - Structure analysis debugging
- `debug_general_search.py` - General search debugging
- `debug_response.html` - Response HTML debugging
- `debug_general_search_response.html` - General search response HTML

### `/tests/`
Test files and testing utilities:
- `test_direct_search.py` - Direct search testing
- `test_direct_simple.py` - Simple direct testing
- `test_go_approach.py` - Google approach testing
- `test_list_search.py` - List search testing
- `test_place_id.py` - Place ID testing
- `test_rpc_search.py` - RPC search testing
- `test_thai_search.py` - Thai language search testing
- `test-kanit-redesign.html` - Kanit redesign test page

### `/responses/`
HTML response files captured during debugging:
- `current_response.html` - Current response capture
- `general_search_response.html` - General search response HTML

### `/patches/`
Patch files created during development:
- `KANIT-REDESIGN-PATCH.patch` - Complete patch file for Kanit redesign

### `/static files/`
Static assets that are no longer used:
- `style.css` - Original stylesheet
- `app.js` - Original JavaScript app

## Important Notes

- These files are kept for historical reference and debugging purposes
- They may contain outdated code or approaches
- The main applications (`app.py` and `app-kanit.py`) do not depend on these files
- Some files may have dependencies that are no longer available in the main project
- Feel free to delete these files if you're confident they won't be needed

## Recovery

If you need to restore any of these files to the main project:
1. Identify the file you need
2. Copy it back to the appropriate location in the main project
3. Update any imports or dependencies as needed
4. Test thoroughly to ensure compatibility

---

**Archive Created**: 2025-11-10
**Purpose**: Clean up main project structure while preserving development history