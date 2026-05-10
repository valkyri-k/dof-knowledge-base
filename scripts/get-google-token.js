/**
 * One-time script to get OAuth2 refresh token for dof.internal@gmail.com
 * Usage: node scripts/get-google-token.js
 * Then copy the printed refresh token to Zeabur GOOGLE_DRIVE_REFRESH_TOKEN
 */

const { google } = require('googleapis');
const readline = require('readline');

const CLIENT_ID = process.env.GOOGLE_DRIVE_CLIENT_ID;
const CLIENT_SECRET = process.env.GOOGLE_DRIVE_CLIENT_SECRET;
const REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob';

if (!CLIENT_ID || !CLIENT_SECRET) {
  console.error('Missing env vars. Run with:');
  console.error('GOOGLE_DRIVE_CLIENT_ID=xxx GOOGLE_DRIVE_CLIENT_SECRET=xxx node scripts/get-google-token.js');
  process.exit(1);
}

const oauth2Client = new google.auth.OAuth2(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI);

const SCOPES = [
  'https://www.googleapis.com/auth/drive',
  'https://www.googleapis.com/auth/documents',
];

const authUrl = oauth2Client.generateAuthUrl({
  access_type: 'offline',
  scope: SCOPES,
  prompt: 'consent',
});

console.log('\n1. Open this URL in browser, login as dof.internal@gmail.com:\n');
console.log(authUrl);
console.log('\n2. After authorizing, paste the code below:\n');

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
rl.question('Code: ', async (code) => {
  rl.close();
  try {
    const { tokens } = await oauth2Client.getToken(code.trim());
    console.log('\n✅ Refresh token:');
    console.log(tokens.refresh_token);
    console.log('\nCopy this to Zeabur GOOGLE_DRIVE_REFRESH_TOKEN');
  } catch (err) {
    console.error('Error:', err.message);
  }
});
