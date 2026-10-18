#!/usr/bin/env node
/**
 * Creates the thesis backlog on GitHub from scripts/github/backlog.json:
 * labels, milestones, epics, tasks (as sub-issues of epics) and a Projects v2 board with fields.
 * Then generates docs/BACKLOG.md and the traceability matrix in docs/WYMAGANIA.md.
 *
 * Idempotent: issues and milestones are matched by title, labels are upserted.
 *
 * Usage:
 *   node scripts/github/create-backlog.mjs --dry-run      # validate and print, no changes
 *   node scripts/github/create-backlog.mjs                # create everything
 *   node scripts/github/create-backlog.mjs --skip-project # issues only
 *   node scripts/github/create-backlog.mjs --docs-only    # regenerate docs from existing issues
 *
 * Requires GitHub CLI authenticated with: gh auth login --scopes "project,repo"
 */
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const BACKLOG_PATH = join(ROOT, "scripts", "github", "backlog.json");
const REQUIREMENTS_PATH = join(ROOT, "docs", "WYMAGANIA.md");
const BACKLOG_MD_PATH = join(ROOT, "docs", "BACKLOG.md");

const args = new Set(process.argv.slice(2));
const DRY_RUN = args.has("--dry-run");
const SKIP_PROJECT = args.has("--skip-project");
const DOCS_ONLY = args.has("--docs-only");
const GH = process.env.GH_PATH || "gh";

const backlog = JSON.parse(readFileSync(BACKLOG_PATH, "utf8"));
const REPO = backlog.repo;
const OWNER = REPO.split("/")[0];
const milestoneByKey = Object.fromEntries(
  backlog.milestones.map((m) => [m.key, m])
);

// ---------------------------------------------------------------- helpers

const TRANSIENT = /HTTP 50[234]|timeout|ECONNRESET|was submitted too quickly/i;

function sleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function gh(ghArgs, { input, json = false, retries = 4 } = {}) {
  // Issue creation is not retried: a 5xx may still have created the issue.
  const retryable = !(ghArgs[0] === "issue" && ghArgs[1] === "create");
  for (let attempt = 0; ; attempt++) {
    try {
      const out = execFileSync(GH, ghArgs, {
        cwd: ROOT,
        encoding: "utf8",
        input,
        stdio: ["pipe", "pipe", "pipe"],
        maxBuffer: 64 * 1024 * 1024
      });
      return json ? JSON.parse(out) : out.trim();
    } catch (e) {
      if (!retryable || attempt >= retries || !TRANSIENT.test(String(e.stderr)))
        throw e;
      const wait = 2000 * 2 ** attempt;
      log(
        `  transient error (${String(e.stderr).trim()}), retry in ${wait / 1000}s`
      );
      sleep(wait);
    }
  }
}

function graphql(query, variables = {}) {
  const ghArgs = ["api", "graphql", "-f", `query=${query}`];
  for (const [k, v] of Object.entries(variables)) {
    ghArgs.push(typeof v === "number" ? "-F" : "-f", `${k}=${v}`);
  }
  return gh(ghArgs, { json: true });
}

function log(msg) {
  console.log(msg);
}

function labelsFor(item, type) {
  return [
    `type:${type}`,
    `area:${item.area}`,
    item.priority && `priority:${item.priority}`,
    item.size && `size:${item.size}`
  ].filter(Boolean);
}

// ---------------------------------------------------------------- validation

function validate() {
  const reqText = readFileSync(REQUIREMENTS_PATH, "utf8");
  const knownReqs = new Set(
    reqText.match(/\b(?:FR|NFR)-[A-Z]+-\d{2}\b/g) || []
  );
  const knownLabels = new Set(backlog.labels.map((l) => l.name));
  const titles = new Set();
  const errors = [];

  for (const epic of backlog.epics) {
    if (!milestoneByKey[epic.milestone])
      errors.push(`Unknown milestone ${epic.milestone} in "${epic.title}"`);
    for (const task of epic.tasks) {
      if (titles.has(task.title))
        errors.push(`Duplicate task title "${task.title}"`);
      titles.add(task.title);
      for (const l of labelsFor(task, task.type))
        if (!knownLabels.has(l))
          errors.push(`Unknown label ${l} in "${task.title}"`);
      for (const r of task.requirements)
        if (!knownReqs.has(r))
          errors.push(`Unknown requirement ${r} in "${task.title}"`);
      if (task.start > task.due)
        errors.push(`Start after due in "${task.title}"`);
    }
  }
  for (const r of Object.keys(backlog.literature))
    if (!knownReqs.has(r))
      errors.push(`Unknown requirement ${r} in literature map`);

  const covered = new Set(
    backlog.epics.flatMap((e) => e.tasks.flatMap((t) => t.requirements))
  );
  const uncovered = [...knownReqs].filter((r) => !covered.has(r));

  if (errors.length) {
    console.error(errors.map((e) => `ERROR: ${e}`).join("\n"));
    process.exit(1);
  }
  const taskCount = backlog.epics.reduce((n, e) => n + e.tasks.length, 0);
  log(
    `Backlog OK: ${backlog.epics.length} epics, ${taskCount} tasks, ${backlog.milestones.length} milestones, ${backlog.labels.length} labels.`
  );
  log(
    `Requirements: ${knownReqs.size} defined, ${covered.size} covered by tasks.`
  );
  if (uncovered.length)
    log(`WARNING: requirements without tasks: ${uncovered.join(", ")}`);
  return knownReqs;
}

// ---------------------------------------------------------------- bodies

function epicBody(epic) {
  const reqs = [...new Set(epic.tasks.flatMap((t) => t.requirements))].sort();
  return `## Goal

${epic.goal}

## Stage Definition of Done

${epic.dod}

## Requirements covered

${reqs.length ? reqs.join(", ") : "—"} (see \`docs/WYMAGANIA.md\`)

## Documentation deliverables

- [ ] \`${epic.docFile}\` contains an entry for every closed task
- [ ] ADRs written for decisions taken in this stage (\`docs/adr/\`)
- [ ] Thesis draft section for this stage (1–2 pages)

## Tasks

Tracked as sub-issues of this epic.

## Stage summary (fill when closing)

_What was done, what moved to later stages, lessons learned._
`;
}

function taskBody(task, epic, epicNumber) {
  const ac = task.acceptance.map((a) => `- [ ] ${a}`).join("\n");
  const reqs = task.requirements.length ? task.requirements.join(", ") : "—";
  const epicRef = epicNumber ? `#${epicNumber}` : epic.title;

  if (task.type === "thesis") {
    return `**Epic:** ${epicRef} · **Stage:** ${epic.milestone}

## Planned content

${ac}

## Sources

- \`docs/RAPORT.md\` (literature review)
- \`docs/implementacja/\`, \`docs/adr/\`, \`docs/experiment/\` (own work)

## Done when

- [ ] Draft written in \`Praca Magisterska.docx\` (Polish)
- [ ] Figures and tables prepared
- [ ] Sent to supervisor and feedback applied
`;
  }

  const docs = [
    `- [ ] Implementation log entry in \`${epic.docFile}\` (section \`### #<this issue> ${task.title}\`)`
  ];
  if (task.type === "spike")
    docs.push(
      "- [ ] Spike note in `docs/spikes/<slug>.md` with verdict (go / no-go / workaround)"
    );
  docs.push(
    task.adr
      ? "- [ ] **ADR required** in `docs/adr/NNNN-*.md`"
      : "- [ ] ADR in `docs/adr/` (if a decision was made)"
  );
  docs.push("- [ ] README / runbook updated (if setup changes)");

  return `**Epic:** ${epicRef} · **Stage:** ${epic.milestone} · **Planned:** ${task.start} → ${task.due}

## Context

Part of ${epicRef}: ${epic.goal}

## Acceptance criteria

${ac}

## Requirements

${reqs}

## Documentation to update

${docs.join("\n")}

## Definition of Done

- [ ] Acceptance criteria met, tests added, CI green
- [ ] Implementation log entry written (what / how / decisions / problems / evidence / thesis link)
- [ ] Requirement IDs listed in the PR; traceability matrix in \`docs/WYMAGANIA.md\` still valid

See \`docs/KONWENCJE.md\` for branch, commit and documentation conventions.
`;
}

// ---------------------------------------------------------------- GitHub: labels & milestones

function syncLabels() {
  for (const l of backlog.labels) {
    if (DRY_RUN) {
      log(`[dry-run] label ${l.name}`);
      continue;
    }
    gh([
      "label",
      "create",
      l.name,
      "--repo",
      REPO,
      "--color",
      l.color,
      "--description",
      l.description,
      "--force"
    ]);
  }
  log(`Labels synced (${backlog.labels.length}).`);
}

function syncMilestones() {
  const existing = DRY_RUN
    ? []
    : gh(["api", `repos/${REPO}/milestones?state=all&per_page=100`], {
        json: true
      });
  const byTitle = Object.fromEntries(existing.map((m) => [m.title, m]));
  for (const m of backlog.milestones) {
    if (byTitle[m.title]) continue;
    const description = `Planned ${m.start} → ${m.due}. See docs/HARMONOGRAM.md.`;
    if (DRY_RUN) {
      log(`[dry-run] milestone ${m.title} (due ${m.due})`);
      continue;
    }
    gh([
      "api",
      "-X",
      "POST",
      `repos/${REPO}/milestones`,
      "-f",
      `title=${m.title}`,
      "-f",
      `due_on=${m.due}T12:00:00Z`,
      "-f",
      `description=${description}`
    ]);
    log(`Milestone created: ${m.title}`);
  }
}

// ---------------------------------------------------------------- GitHub: issues

function listIssues() {
  const issues = gh(
    [
      "issue",
      "list",
      "--repo",
      REPO,
      "--state",
      "all",
      "--limit",
      "1000",
      "--json",
      "number,title,url"
    ],
    { json: true }
  );
  return Object.fromEntries(issues.map((i) => [i.title, i]));
}

function createIssue({ title, body, labels, milestone }) {
  const url = gh(
    [
      "issue",
      "create",
      "--repo",
      REPO,
      "--title",
      title,
      "--body-file",
      "-",
      "--label",
      labels.join(","),
      "--milestone",
      milestone
    ],
    { input: body }
  );
  const number = Number(url.trim().split("/").pop());
  log(`  #${number} ${title}`);
  return { number, title, url: url.trim() };
}

function issueDatabaseId(number) {
  return Number(gh(["api", `repos/${REPO}/issues/${number}`, "--jq", ".id"]));
}

function linkSubIssues(epicNumber, childNumbers) {
  const current = gh(
    ["api", `repos/${REPO}/issues/${epicNumber}/sub_issues?per_page=100`],
    { json: true }
  );
  const linked = new Set(current.map((i) => i.number));
  for (const n of childNumbers) {
    if (linked.has(n)) continue;
    gh([
      "api",
      "-X",
      "POST",
      `repos/${REPO}/issues/${epicNumber}/sub_issues`,
      "-F",
      `sub_issue_id=${issueDatabaseId(n)}`
    ]);
  }
}

function syncIssues() {
  const existing = DRY_RUN ? {} : listIssues();
  const result = []; // { epic, epicIssue, tasks: [{ task, issue }] }

  for (const epic of backlog.epics) {
    const milestone = milestoneByKey[epic.milestone].title;
    log(`${epic.title}`);
    let epicIssue = existing[epic.title];
    if (!epicIssue) {
      epicIssue = DRY_RUN
        ? { number: null, title: epic.title }
        : createIssue({
            title: epic.title,
            body: epicBody(epic),
            labels: ["type:epic", `area:${epic.area}`],
            milestone
          });
    }

    const tasks = [];
    for (const task of epic.tasks) {
      let issue = existing[task.title];
      if (!issue) {
        if (DRY_RUN) {
          log(
            `  [dry-run] ${task.type.padEnd(8)} ${task.priority} ${task.size} ${task.start}→${task.due}  ${task.title}`
          );
          issue = { number: null, title: task.title };
        } else {
          issue = createIssue({
            title: task.title,
            body: taskBody(task, epic, epicIssue.number),
            labels: labelsFor(task, task.type),
            milestone
          });
        }
      }
      tasks.push({ task, issue });
    }

    if (!DRY_RUN)
      linkSubIssues(
        epicIssue.number,
        tasks.map((t) => t.issue.number)
      );
    result.push({ epic, epicIssue, tasks });
  }
  return result;
}

// ---------------------------------------------------------------- GitHub: project v2

const PROJECT_FIELDS = [
  {
    name: "Stage",
    type: "SINGLE_SELECT",
    options: () => backlog.milestones.map((m) => m.key)
  },
  {
    name: "Work type",
    type: "SINGLE_SELECT",
    options: () => [
      "epic",
      "feature",
      "chore",
      "spike",
      "docs",
      "research",
      "thesis"
    ]
  },
  {
    name: "Priority",
    type: "SINGLE_SELECT",
    options: () => ["P1", "P2", "P3"]
  },
  { name: "Size", type: "SINGLE_SELECT", options: () => ["S", "M", "L"] },
  { name: "Start date", type: "DATE" },
  { name: "Target date", type: "DATE" }
];

function ensureProject() {
  const list = gh(
    ["project", "list", "--owner", OWNER, "--limit", "100", "--format", "json"],
    { json: true }
  );
  let project = list.projects.find((p) => p.title === backlog.project.title);
  if (!project) {
    project = gh(
      [
        "project",
        "create",
        "--owner",
        OWNER,
        "--title",
        backlog.project.title,
        "--format",
        "json"
      ],
      { json: true }
    );
    gh([
      "project",
      "edit",
      String(project.number),
      "--owner",
      OWNER,
      "--description",
      backlog.project.description
    ]);
    log(`Project created: ${project.url}`);
  }
  try {
    gh([
      "project",
      "link",
      String(project.number),
      "--owner",
      OWNER,
      "--repo",
      REPO
    ]);
  } catch {
    // already linked
  }
  return project;
}

function ensureFields(project) {
  const listFields = () =>
    gh(
      [
        "project",
        "field-list",
        String(project.number),
        "--owner",
        OWNER,
        "--limit",
        "100",
        "--format",
        "json"
      ],
      { json: true }
    ).fields;
  let fields = listFields();
  for (const f of PROJECT_FIELDS) {
    if (fields.some((x) => x.name === f.name)) continue;
    const fieldArgs = [
      "project",
      "field-create",
      String(project.number),
      "--owner",
      OWNER,
      "--name",
      f.name,
      "--data-type",
      f.type
    ];
    if (f.options)
      fieldArgs.push("--single-select-options", f.options().join(","));
    gh(fieldArgs);
    log(`Project field created: ${f.name}`);
  }
  fields = listFields();
  return Object.fromEntries(fields.map((f) => [f.name, f]));
}

function listProjectItems(project) {
  const list = gh(
    [
      "project",
      "item-list",
      String(project.number),
      "--owner",
      OWNER,
      "--limit",
      "1000",
      "--format",
      "json"
    ],
    { json: true }
  );
  return Object.fromEntries(
    list.items
      .filter((i) => i.content?.number)
      .map((i) => [i.content.number, i.id])
  );
}

function addToProject(project, issues) {
  // GitHub's built-in workflow auto-adds sub-issues once their epic is in the project,
  // so "already exists" is expected; such items are resolved from the item list.
  const items = listProjectItems(project);
  for (const issue of issues) {
    if (items[issue.number]) continue;
    try {
      const item = gh(
        [
          "project",
          "item-add",
          String(project.number),
          "--owner",
          OWNER,
          "--url",
          issue.url,
          "--format",
          "json"
        ],
        { json: true }
      );
      items[issue.number] = item.id;
    } catch (e) {
      if (!String(e.stderr).includes("already exists")) throw e;
    }
  }
  return { ...listProjectItems(project), ...items };
}

function setFieldValues(project, fields, assignments) {
  // assignments: [{ itemId, values: { fieldName: value } }]
  const mutations = [];
  for (const { itemId, values } of assignments) {
    for (const [name, value] of Object.entries(values)) {
      const field = fields[name];
      if (!field || value == null) continue;
      let valueLiteral;
      if (field.type === "ProjectV2SingleSelectField") {
        const option = field.options.find((o) => o.name === value);
        if (!option) continue;
        valueLiteral = `{singleSelectOptionId: "${option.id}"}`;
      } else {
        valueLiteral = `{date: "${value}"}`;
      }
      mutations.push(
        `m${mutations.length}: updateProjectV2ItemFieldValue(input: {projectId: "${project.id}", itemId: "${itemId}", fieldId: "${field.id}", value: ${valueLiteral}}) { clientMutationId }`
      );
    }
  }
  const BATCH = 20;
  for (let i = 0; i < mutations.length; i += BATCH) {
    graphql(`mutation { ${mutations.slice(i, i + BATCH).join("\n")} }`);
  }
  log(`Project field values set (${mutations.length}).`);
}

function syncProject(result) {
  const project = ensureProject();
  const fields = ensureFields(project);
  const all = result.flatMap((r) => [
    r.epicIssue,
    ...r.tasks.map((t) => t.issue)
  ]);
  const items = addToProject(project, all);
  log(`Project items: ${Object.keys(items).length}.`);

  const assignments = [];
  for (const { epic, epicIssue, tasks } of result) {
    const m = milestoneByKey[epic.milestone];
    const starts = tasks.map((t) => t.task.start).sort();
    const dues = tasks.map((t) => t.task.due).sort();
    assignments.push({
      itemId: items[epicIssue.number],
      values: {
        Stage: epic.milestone,
        "Work type": "epic",
        Priority: "P1",
        "Start date": starts[0] || m.start,
        "Target date": dues.at(-1) || m.due
      }
    });
    for (const { task, issue } of tasks) {
      assignments.push({
        itemId: items[issue.number],
        values: {
          Stage: epic.milestone,
          "Work type": task.type,
          Priority: task.priority,
          Size: task.size,
          "Start date": task.start,
          "Target date": task.due
        }
      });
    }
  }
  setFieldValues(project, fields, assignments);
  return project;
}

// ---------------------------------------------------------------- docs generation

function issueLink(issue) {
  return issue.number ? `[#${issue.number}](${issue.url})` : "—";
}

function writeBacklogMd(result, project) {
  const lines = [
    "# Backlog",
    "",
    "> Plik generowany przez `scripts/github/create-backlog.mjs` z `scripts/github/backlog.json` — nie edytować ręcznie.",
    `> Status zadań: ${project ? `[GitHub Project](${project.url})` : "GitHub Project"} · Konwencje: [KONWENCJE.md](KONWENCJE.md) · Wymagania: [WYMAGANIA.md](WYMAGANIA.md)`,
    ""
  ];
  for (const { epic, epicIssue, tasks } of result) {
    const m = milestoneByKey[epic.milestone];
    lines.push(
      `## ${m.title} (${m.start} → ${m.due}) — ${issueLink(epicIssue)}`,
      "",
      epic.goal,
      ""
    );
    lines.push(
      "| Issue | Zadanie | Typ | Prio | Rozmiar | Start | Termin | Wymagania |"
    );
    lines.push(
      "| ----- | ------- | --- | ---- | ------- | ----- | ------ | --------- |"
    );
    for (const { task, issue } of tasks) {
      lines.push(
        `| ${issueLink(issue)} | ${task.title} | ${task.type} | ${task.priority} | ${task.size} | ${task.start} | ${task.due} | ${task.requirements.join(", ") || "—"} |`
      );
    }
    lines.push("");
  }
  writeFileSync(BACKLOG_MD_PATH, lines.join("\n"));
  log("docs/BACKLOG.md written.");
}

function writeTraceability(result, knownReqs) {
  const byReq = {};
  for (const { tasks } of result) {
    for (const { task, issue } of tasks) {
      for (const r of task.requirements) (byReq[r] ||= []).push(issue);
    }
  }
  const order = (id) => id.replace(/\d+$/, (d) => d.padStart(3, "0"));
  const rows = [...knownReqs]
    .sort((a, b) => order(a).localeCompare(order(b)))
    .map(
      (r) =>
        `| ${r} | ${(byReq[r] || []).map(issueLink).join(", ") || "_brak_"} | ${backlog.literature[r] || "—"} |`
    );
  const table = [
    "",
    "| Wymaganie | Issues | Literatura |",
    "| --------- | ------ | ---------- |",
    ...rows,
    ""
  ].join("\n");

  const text = readFileSync(REQUIREMENTS_PATH, "utf8");
  const updated = text.replace(
    /(<!-- TRACEABILITY:START -->)[\s\S]*?(<!-- TRACEABILITY:END -->)/,
    `$1\n${table}\n$2`
  );
  writeFileSync(REQUIREMENTS_PATH, updated);
  log("Traceability matrix in docs/WYMAGANIA.md updated.");
}

// ---------------------------------------------------------------- main

function main() {
  const knownReqs = validate();
  if (!DRY_RUN) gh(["auth", "status"]);

  if (DOCS_ONLY) {
    const existing = listIssues();
    const result = backlog.epics.map((epic) => ({
      epic,
      epicIssue: existing[epic.title] || { number: null },
      tasks: epic.tasks.map((task) => ({
        task,
        issue: existing[task.title] || { number: null }
      }))
    }));
    const list = gh(
      [
        "project",
        "list",
        "--owner",
        OWNER,
        "--limit",
        "100",
        "--format",
        "json"
      ],
      { json: true }
    );
    writeBacklogMd(
      result,
      list.projects.find((p) => p.title === backlog.project.title)
    );
    writeTraceability(result, knownReqs);
    return;
  }

  syncLabels();
  syncMilestones();
  const result = syncIssues();
  if (DRY_RUN) {
    log("\nDry run finished — nothing was changed.");
    return;
  }
  const project = SKIP_PROJECT ? null : syncProject(result);
  writeBacklogMd(result, project);
  writeTraceability(result, knownReqs);
  if (project) log(`\nDone. Project: ${project.url}`);
}

main();
