import { google } from 'googleapis';
import { CONFIG_CREDENTIALS as _sheets_creds, choose_tp } from "./utils.js";

// Load service account credentials
const auth = new google.auth.GoogleAuth({
  keyFile: `../credentials/${choose_tp('credentials-test.json', 'credentials.json')}`,
  scopes: ['https://www.googleapis.com/auth/spreadsheets'],
});

// get spreadsheet ID and modification cell range
const range = _sheets_creds['cell-range']; // Update this range as needed
const spreadsheetId = _sheets_creds[choose_tp('test-spreadsheet-id', 'spreadsheet-id')];

// add a single row at the end of the specified google sheet.
export async function addRowToGoogleSheet(values) {
  try {
    const sheets = google.sheets({ version: 'v4', auth: await auth.getClient() });
    
    const request = {
      spreadsheetId,
      range,
      valueInputOption: 'USER_ENTERED',
      resource: {
        values: [values],
      },
    };
    
    const response = await sheets.spreadsheets.values.append(request);
    console.log(`Last Update: [${values}]`);
  } catch (error) {
    console.error('Error inserting data:', error);
  }
}
