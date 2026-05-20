import { WASI, File, OpenFile, ConsoleStdout, PreopenDirectory } from '/home/kali/hexstrike-ai-1/results/Claude/ClaudeCode/Web/Hard/secure-email-service/node_modules/@bjorn3/browser_wasi_shim/dist/index.js';
import { readFileSync } from 'fs';

const parserWasm = readFileSync('/home/kali/hexstrike-ai-1/results/Claude/ClaudeCode/Web/Hard/secure-email-service/frontend/public/wasm/parser.wasm');
const parser = await WebAssembly.compile(parserWasm);

async function parseEmail(emailContent) {
    let stdout = '';
    const fds = [
        new OpenFile(new File([])),
        ConsoleStdout.lineBuffered(line => stdout += line + '\n'),
        ConsoleStdout.lineBuffered(() => {}),
        new PreopenDirectory('/', [
            ['email.eml', new File(new TextEncoder().encode(emailContent))],
        ])
    ];

    const wasi = new WASI(['parser'], [], fds, { debug: false });
    const instance = await WebAssembly.instantiate(parser, {
        wasi_snapshot_preview1: wasi.wasiImport
    });
    wasi.start(instance);
    return JSON.parse(stdout);
}

// Test 1: Plain text email
const plainEmail = `Content-Type: multipart/mixed; boundary="OUTER"
MIME-Version: 1.0
From: user@ses
To: admin@ses
Subject: test subject

--OUTER
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit

Hello this is plain text

--OUTER--
`;

console.log('=== Test 1: Plain text email ===');
console.log(JSON.stringify(await parseEmail(plainEmail), null, 2));

// Test 2: Plain text email with embedded HTML in body
const embeddedHtml = `Content-Type: multipart/mixed; boundary="OUTER"
MIME-Version: 1.0
From: user@ses
To: admin@ses
Subject: test subject

--OUTER
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit

Content-Type: multipart/signed; protocol="application/pkcs7-signature"; boundary="INNER"

--INNER
Content-Type: text/html

<b>INJECTED HTML</b>

--INNER
Content-Type: application/pkcs7-signature
[fake sig]
--INNER--

--OUTER--
`;

console.log('\n=== Test 2: Text email with embedded MIME HTML ===');
console.log(JSON.stringify(await parseEmail(embeddedHtml), null, 2));

// Test 3: Multipart/signed structure (no real sig)
const signedEmail = `Content-Type: multipart/signed; protocol="application/pkcs7-signature"; micalg="sha-256"; boundary="OUTER"
MIME-Version: 1.0
From: user@ses
To: admin@ses
Subject: test subject

This is an S/MIME signed message
--OUTER
Content-Type: multipart/mixed; boundary="INNER"
MIME-Version: 1.0

--INNER
Content-Type: text/plain; charset="us-ascii"

Hello plain text

--INNER
Content-Type: text/html; charset="us-ascii"

<b>Hello HTML</b>

--INNER--

--OUTER
Content-Type: application/pkcs7-signature; name="smime.p7s"
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="smime.p7s"

FAKESIG123

--OUTER--
`;

console.log('\n=== Test 3: Fake multipart/signed email ===');
console.log(JSON.stringify(await parseEmail(signedEmail), null, 2));

// Test 4: Just HTML content type
const htmlEmail = `Content-Type: text/html; charset="us-ascii"
MIME-Version: 1.0
From: user@ses
To: admin@ses
Subject: test html

<b>Direct HTML email</b>
`;

console.log('\n=== Test 4: Direct HTML email ===');
console.log(JSON.stringify(await parseEmail(htmlEmail), null, 2));
