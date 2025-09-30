"""
Test Google Sheets Integration
This script tests the Google Sheets authentication and basic operations
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.google_sheets import GoogleSheetsManager


def test_authentication():
    """Test Google Sheets authentication"""
    print("=" * 60)
    print("Testing Google Sheets Authentication")
    print("=" * 60)
    
    credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')
    token_path = os.path.join(os.path.dirname(__file__), '..', 'token.json')
    
    print(f"\nCredentials file: {credentials_path}")
    print(f"Token file: {token_path}")
    
    if not os.path.exists(credentials_path):
        print("\n❌ ERROR: credentials.json not found!")
        print("Please download it from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Select your project")
        print("3. Go to APIs & Services > Credentials")
        print("4. Download OAuth 2.0 Client ID credentials")
        print("5. Save as credentials.json in the project root")
        return False
    
    print("\n✓ credentials.json found")
    
    # Check if token exists and warn about re-authentication
    if os.path.exists(token_path):
        print("\n⚠️  Note: token.json exists from previous authentication")
        print("If you see scope errors, the token will be automatically regenerated")
    
    try:
        print("\n⏳ Authenticating with Google Sheets API...")
        print("(A browser window will open if this is your first time)")
        
        sheets_manager = GoogleSheetsManager(credentials_path, token_path)
        
        print("✓ Authentication successful!")
        print(f"✓ Token saved to: {token_path}")
        
        return sheets_manager
    
    except Exception as e:
        print(f"\n❌ Authentication failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_create_spreadsheet(sheets_manager):
    """Test creating a Google Spreadsheet"""
    print("\n" + "=" * 60)
    print("Testing Spreadsheet Creation")
    print("=" * 60)
    
    try:
        print("\n⏳ Creating test spreadsheet...")
        
        result = sheets_manager.create_spreadsheet("Test Spreadsheet - French Novel Processor")
        
        print(f"\n✓ Spreadsheet created successfully!")
        print(f"📊 Spreadsheet ID: {result['spreadsheet_id']}")
        print(f"🔗 URL: {result['spreadsheet_url']}")
        
        return result['spreadsheet_id'], result['spreadsheet_url']
    
    except Exception as e:
        print(f"\n❌ Failed to create spreadsheet: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def test_write_data(sheets_manager, spreadsheet_id):
    """Test writing data to a spreadsheet"""
    print("\n" + "=" * 60)
    print("Testing Data Writing")
    print("=" * 60)
    
    try:
        print("\n⏳ Writing test data...")
        
        # Sample data
        data = [
            ['Row', 'Sentence', 'Original', 'Method', 'Word_Count'],
            [1, 'Le chat dort.', 'Le chat dort paisiblement sur le canapé.', 'AI-Rewritten', 3],
            [2, 'Il fait beau.', 'Il fait beau aujourd\'hui.', 'Direct', 3],
            [3, 'La voiture est rouge.', 'La voiture garée là-bas est rouge.', 'Mechanical', 4]
        ]
        
        sheets_manager.write_data(spreadsheet_id, 'Sheet1', data)
        
        print("✓ Data written successfully!")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Failed to write data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_formatting(sheets_manager, spreadsheet_id):
    """Test applying formatting"""
    print("\n" + "=" * 60)
    print("Testing Formatting")
    print("=" * 60)
    
    try:
        print("\n⏳ Applying formatting...")
        
        sheet_id = sheets_manager.get_sheet_id(spreadsheet_id, 'Sheet1')
        
        if sheet_id is None:
            print("❌ Could not find sheet ID")
            return False
        
        # Apply header formatting
        sheets_manager.apply_header_formatting(
            spreadsheet_id,
            sheet_id,
            5,  # 5 columns
            {'red': 0.27, 'green': 0.45, 'blue': 0.77}  # Blue
        )
        print("  ✓ Header formatting applied")
        
        # Apply borders
        sheets_manager.apply_borders(spreadsheet_id, sheet_id, 4, 5)
        print("  ✓ Borders applied")
        
        # Freeze header row
        sheets_manager.freeze_rows(spreadsheet_id, sheet_id, 1)
        print("  ✓ Header row frozen")
        
        # Set column widths
        sheets_manager.set_column_widths(
            spreadsheet_id,
            sheet_id,
            {0: 60, 1: 400, 2: 400, 3: 150, 4: 100}
        )
        print("  ✓ Column widths set")
        
        print("\n✓ All formatting applied successfully!")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Failed to apply formatting: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n🚀 Starting Google Sheets Integration Tests\n")
    
    # Test 1: Authentication
    sheets_manager = test_authentication()
    if not sheets_manager:
        print("\n❌ Tests failed at authentication stage")
        return
    
    # Test 2: Create spreadsheet
    spreadsheet_id, spreadsheet_url = test_create_spreadsheet(sheets_manager)
    if not spreadsheet_id:
        print("\n❌ Tests failed at spreadsheet creation stage")
        return
    
    # Test 3: Write data
    if not test_write_data(sheets_manager, spreadsheet_id):
        print("\n❌ Tests failed at data writing stage")
        return
    
    # Test 4: Apply formatting
    if not test_formatting(sheets_manager, spreadsheet_id):
        print("\n❌ Tests failed at formatting stage")
        return
    
    # Success!
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print(f"\n📊 View your test spreadsheet:")
    print(f"🔗 {spreadsheet_url}")
    print("\nYou can now use Google Sheets integration in the web interface!")
    print("=" * 60)


if __name__ == '__main__':
    main()
