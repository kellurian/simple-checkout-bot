# Mock Checkout Page

This is a mock implementation of the checkout page that simulates the target page structure and behavior for testing purposes.

## Structure

- `server.py` - Python HTTP server with auto-reload capability
- `index.html` - Mock checkout page with matching element structure

## Element Structure

The page implements the following key elements with identical structure to the target:

1. "Proceed to pay" button
```css
button.a-button.m-cartActionBar__button.-regular.-transaction.-filled.-withShapes.-shapecorner.-shapePadding24.-leftPadding24[data-cy-id='__place-order-button']
```

2. Terms checkbox
```css
div.a-checkboxDisplay.a-checkbox__wrapper.-interactive[data-cy-id='checkbox__display']
```

3. "I agree" button
```css
button.a-button.m-modalFooter__primaryButton.-regular.-interaction.-filled.-withShapes.-shapecorner.-shapePadding24.-leftPadding24[data-cy-id='modal_footer__primary_button']
```

4. Out-of-stock message
```css
p.m-toast__title.a-fontStyle.-emphasis-3.-no-rich-text[data-cy-id='toast__title']
```

## Usage

1. Start the server:
```bash
python server.py
```

2. Access the page at `http://localhost:8000`

## Testing Scenarios

The page provides JavaScript functions for testing different states:

- `toggleOutOfStock()` - Toggle out-of-stock status
- `simulateSuccess()` - Simulate successful checkout flow
- `triggerError()` - Trigger out-of-stock error state

## Flow States

1. Normal Flow:
   - Check terms checkbox
   - Click "Proceed to pay"
   - Success message appears

2. Terms Modal:
   - Click "Proceed to pay" without checking terms
   - Terms modal appears
   - Click "I agree" to accept

3. Out of Stock:
   - Toggle out of stock state
   - Click "Proceed to pay"
   - Out of stock message appears

## Auto-reload Feature

The server implements auto-reload capability through HTTP headers, allowing for immediate reflection of changes during development.

## Success Criteria Verification

- [x] Element structure matches target exactly
- [x] All test scenarios can be simulated
- [x] Page accessible via localhost:8000
- [x] JavaScript state changes work correctly
- [x] Server starts/stops cleanly

## Testing Guide

1. Manual Tests:
   - Start server and verify page loads at localhost:8000
   - Verify all elements are present and styled correctly
   - Test each interaction flow (normal, terms, out-of-stock)
   - Verify state changes work through browser console
   - Test server shutdown with Ctrl+C

2. Element Structure Tests:
   - Verify element classes match target
   - Verify data attributes are present
   - Check element nesting hierarchy
   - Validate button structures

3. Visual Tests:
   - Verify button styling
   - Check modal appearance
   - Verify toast message visibility
   - Validate responsive behavior
