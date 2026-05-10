// SETUP: Replace with your Google Spreadsheet ID.
// Find it in the sheet URL: docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
const SPREADSHEET_ID = '1Jn6mYpmr9PukyJmzvnkeFNtB4pFfvgVt3vvxJyL45v4';

function doGet(e) {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);

  const invSheet = ss.getSheetByName('Inventory');
  const invData = invSheet.getDataRange().getValues();
  const invHeaders = invData[0];
  const inventory = invData.slice(1)
    .filter(row => row[0] !== '')  // skip empty rows
    .map(row => Object.fromEntries(invHeaders.map((h, i) => [h, row[i]])));

  const boxSheet = ss.getSheetByName('Box names');
  const boxData = boxSheet.getDataRange().getValues();
  const boxHeaders = boxData[0];
  const boxes = boxData.slice(1)
    .filter(row => row[0] !== '')  // skip empty rows
    .map(row => Object.fromEntries(boxHeaders.map((h, i) => [h, row[i]])));

  const payload = JSON.stringify({
    inventory: inventory,
    boxes: boxes,
    fetchedAt: new Date().toISOString()
  });

  return ContentService
    .createTextOutput(payload)
    .setMimeType(ContentService.MimeType.JSON);
}
