// ComplianceKI Scanner — VSCode Extension
// Scans the workspace against ComplianceKIbot.de and shows findings as diagnostics.
const vscode = require('vscode');
const { execFile } = require('child_process');
const { promisify } = require('util');

const execFileP = promisify(execFile);
const RESULTS_VIEW = 'complianceki.results';

let ctx = null;
let diag = null;
let output = null;

function activate(context) {
    ctx = context;
    diag = vscode.languages.createDiagnosticCollection('complianceki');
    output = vscode.window.createOutputChannel('ComplianceKI');
    output.appendLine('ComplianceKI Scanner ready.');

    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBar.text = '$(shield) ComplianceKI';
    statusBar.command = 'complianceki.viewResults';
    statusBar.tooltip = 'ComplianceKI Scanner — click to view results';
    statusBar.show();

    context.subscriptions.push(
        diag,
        output,
        statusBar,
        vscode.commands.registerCommand('complianceki.scanWorkspace', scanWorkspace),
        vscode.commands.registerCommand('complianceki.scanFile', scanFile),
        vscode.commands.registerCommand('complianceki.viewResults', () => output.show(true)),
        vscode.commands.registerCommand('complianceki.setApiKey', setApiKey),
    );
}

function deactivate() {
    if (diag) diag.dispose();
}

/* ── config / secrets ─────────────────────────────────────────────── */

function baseUrl() {
    return vscode.workspace.getConfiguration('complianceki').get('apiUrl', 'https://api.compliancekibot.de');
}

function mode() {
    return vscode.workspace.getConfiguration('complianceki').get('mode', 'assessment_only');
}

function failOn() {
    return vscode.workspace.getConfiguration('complianceki').get('failOnSeverity', 'none');
}

async function apiKey() {
    let value = await ctx.secrets.get('complianceki.apiKey');
    if (value) return value;
    value = await vscode.window.showInputBox({ prompt: 'Enter your ComplianceKIbot.de API key', password: true, ignoreFocusOut: true, placeHolder: 'ck_…' });
    if (value) await ctx.secrets.store('complianceki.apiKey', value);
    return value || '';
}

/* ── api helper ───────────────────────────────────────────────────── */

async function callApi(path, opts = {}) {
    const key = await apiKey();
    if (!key) throw new Error('No ComplianceKI API key. Run "ComplianceKI: Set API Key".');
    const res = await fetch(baseUrl() + path, {
        headers: { 'X-API-Key': key, 'Content-Type': 'application/json' },
        ...opts,
    });
    const text = await res.text();
    if (!res.ok) throw new Error(`ComplianceKI API ${res.status}: ${text}`);
    return text ? JSON.parse(text) : null;
}

async function gitRemote(folder) {
    try {
        const { stdout } = await execFileP('git', ['-C', folder.fsPath, 'remote', 'get-url', 'origin']);
        return stdout.trim();
    } catch {
        return folder.fsPath;
    }
}

/* ── commands ─────────────────────────────────────────────────────── */

async function scanWorkspace() {
    const folder = vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders[0];
    if (!folder) return vscode.window.showErrorMessage('Open a workspace folder first.');
    const repoRef = await gitRemote(folder);
    await runScan(repoRef, folder);
}

async function scanFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return vscode.window.showErrorMessage('No active editor.');
    const folder = vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders[0];
    const repoRef = `file://${editor.document.fileName}`;
    await runScan(repoRef, folder || { uri: vscode.Uri.file(editor.document.fileName), fsPath: folder ? folder.fsPath : '' });
}

async function setApiKey() {
    const key = await vscode.window.showInputBox({ prompt: 'Enter your ComplianceKIbot.de API key', password: true, ignoreFocusOut: true, placeHolder: 'ck_…' });
    if (key) {
        await ctx.secrets.store('complianceki.apiKey', key);
        vscode.window.showInformationMessage('ComplianceKI API key saved.');
    }
}

async function runScan(repoRef, folder) {
    await vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: 'ComplianceKI Scan', cancellable: false }, async (progress) => {
        progress.report({ message: 'Creating scan run…' });
        const run = await callApi('/api/v1/runs', { method: 'POST', body: JSON.stringify({ repo_ref: repoRef, mode: mode() }) });

        progress.report({ message: 'Scanning…' });
        let status = run && run.status;
        for (let i = 0; i < 60 && status !== 'completed' && status !== 'failed'; i++) {
            await new Promise((r) => setTimeout(r, 10000));
            const d = await callApi(`/api/v1/runs/${run.id}`);
            status = d.status;
        }
        if (status !== 'completed') {
            output.show(true);
            output.appendLine(`Scan did not complete: ${status}`);
            return vscode.window.showErrorMessage(`ComplianceKI scan did not complete (${status}).`);
        }

        const findings = (await callApi(`/api/v1/findings?run_id=${run.id}&limit=500`)) || [];
        diag.clear();
        output.clear();
        output.appendLine(`ComplianceKI scan — ${repoRef}`);
        output.appendLine(`Mode: ${mode()} · ${findings.length} finding(s)`);

        const threshold = { none: 5, critical: 0, high: 1 }[failOn()] ?? 5;
        const severityRank = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
        const seen = new Set();

        for (const f of findings) {
            const file = f.file_path || '';
            const line = `[${f.severity}] ${f.title} @ ${file || '?'} (score ${f.risk_score ?? 'n/a'})`;
            output.appendLine(line);
            if (!file) continue;

            const uri = folder.fsPath ? vscode.Uri.joinPath(folder.uri, file) : vscode.Uri.file(file);
            if (seen.has(uri.toString())) continue;
            seen.add(uri.toString());

            const rank = severityRank[f.severity] ?? 4;
            if ((failOn() === 'none' || rank <= threshold)) {
                const severity = rank <= 1 ? vscode.DiagnosticSeverity.Error : rank === 2 ? vscode.DiagnosticSeverity.Warning : vscode.DiagnosticSeverity.Information;
                diag.set(uri, [new vscode.Diagnostic(new vscode.Range(0, 0, 0, 0), `[${f.severity}] ${f.title}`, severity)]);
            }
        }

        output.show(true);
        vscode.window.showInformationMessage(`ComplianceKI: ${findings.length} finding(s) — see output.`);
    });
}

module.exports = { activate, deactivate };
