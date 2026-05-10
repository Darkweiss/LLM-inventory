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

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents);
    const boxId    = body.box;
    const itemName = (body.item_name || '').trim();
    const notes    = (body.notes     || '').trim();
    const quantity = body.quantity;

    if (boxId === undefined || boxId === null || boxId === '') {
      return _json({ok: false, error: 'box is required'});
    }
    if (!itemName) {
      return _json({ok: false, error: 'item_name is required'});
    }

    const ss = SpreadsheetApp.openById(SPREADSHEET_ID);

    const boxSheet   = ss.getSheetByName('Box names');
    const boxData    = boxSheet.getDataRange().getValues();
    const boxHeaders = boxData[0];
    const idCol      = boxHeaders.indexOf('Box ID');
    const nameCol    = boxHeaders.indexOf('Box Name');
    const locCol     = boxHeaders.indexOf('Location');

    const boxRow = boxData.slice(1).find(row => String(row[idCol]) === String(boxId));
    if (!boxRow) {
      return _json({ok: false, error: 'Box ID ' + boxId + ' not found'});
    }

    const numericId = Number(boxId);
    const invSheet  = ss.getSheetByName('Inventory');
    let qtyCell = '';
    if (quantity !== undefined && quantity !== null && quantity !== '') {
      const numericQty = Number(quantity);
      qtyCell = isNaN(numericQty) ? quantity : numericQty;
    }

    invSheet.appendRow([
      isNaN(numericId) ? boxId : numericId,
      boxRow[nameCol],
      boxRow[locCol],
      itemName,
      '',
      '',
      qtyCell,
      notes,
    ]);

    return _json({ok: true, box: boxId, item_name: itemName});
  } catch (err) {
    return _json({ok: false, error: err.message});
  }
}

function _json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
